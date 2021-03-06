from django_fields.fields import EncryptedCharField
from django.utils.timezone import now

from services.models import APICall
from credentials.models import BaseCredential, BaseBalance, BaseSentBTC, BaseAddressFromCredential
from bitcoins.models import BTCTransaction

from bitcoins.BCAddressField import is_valid_btc_address

from bitcash.settings import BCI_SECRET_KEY

import requests
import json
import urllib


class BCICredential(BaseCredential):

    username = EncryptedCharField(max_length=64, blank=False, null=False, db_index=True)
    main_password = EncryptedCharField(max_length=128, blank=False, null=False, db_index=True)
    second_password = EncryptedCharField(max_length=128, blank=True, null=True, db_index=True)

    def get_credential_abbrev(self):
        return 'BCI'

    def get_credential_to_display(self):
        return 'blockchain.info'

    def get_login_link(self):
        return 'https://blockchain.info/wallet/%s' % self.username

    def is_blockchain_credential(self):
        return True

    def get_balance(self):
        """
        Return acount balance in satoshis
        """

        BASE_URL = 'https://blockchain.info/merchant/%s/balance?password=%s'
        BALANCE_URL = BASE_URL % (self.username, urllib.quote(self.main_password))

        r = requests.get(BALANCE_URL)

        # Log the API call
        APICall.objects.create(
            api_name=APICall.BLOCKCHAIN_WALLET_BALANCE,
            url_hit=BALANCE_URL,
            response_code=r.status_code,
            post_params=None,
            api_results=r.content,
            merchant=self.merchant,
            credential=self)

        status_code_is_valid = self.handle_status_code(r.status_code)

        if not status_code_is_valid:
            return False

        resp_json = json.loads(r.content)

        if 'error' in resp_json:
            self.mark_failure()
            print 'Blockchain Error: %s' % resp_json['error']
            return False

        satoshis = int(resp_json['balance'])

        # Record the balance results
        BaseBalance.objects.create(satoshis=satoshis, credential=self)

        return satoshis

    def request_cashout(self, satoshis_to_sell, limit_order_price=None):
        raise Exception('Not Possible')

    def send_btc(self, satoshis_to_send, destination_btc_address):
        """
        Returns a tuple of the form (some or all may be none):
            btc_txn, sent_btc_obj, api_call, err_str
        """

        msg = '%s is not a valid bitcoin address' % destination_btc_address
        assert is_valid_btc_address(destination_btc_address), msg

        BASE_URL = 'https://blockchain.info/merchant/%s/payment?password=%s&to=%s&amount=%s&shared=false'
        SEND_URL = BASE_URL % (self.username, urllib.quote(self.main_password),
                destination_btc_address, satoshis_to_send)

        if self.second_password:
            SEND_URL += '&second_password=%s' % urllib.quote(self.second_password)

        r = requests.get(SEND_URL)

        # Log the API call
        api_call = APICall.objects.create(
            api_name=APICall.BLOCKCHAIN_WALLET_SEND_BTC,
            url_hit=SEND_URL,
            response_code=r.status_code,
            post_params=None,
            api_results=r.content,
            merchant=self.merchant,
            credential=self)

        self.handle_status_code(r.status_code)

        resp_json = json.loads(r.content)

        if 'error' in resp_json:
            # TODO: this assumes all error messages here are safe to display to the user
            return None, None, api_call, resp_json['error']

        if 'tx_hash' not in resp_json:
            # TODO: this assumes all error messages here are safe to display to the user
            return None, None, api_call, 'No Transaction Hash Received from Blockchain.Info'

        tx_hash = resp_json['tx_hash']

        # Record the Send
        sent_btc_obj = BCISentBTC.objects.create(
                credential=self,
                satoshis=satoshis_to_send,
                destination_btc_address=destination_btc_address,
                txn_hash=tx_hash,
                )

        return BTCTransaction.objects.create(
            txn_hash=tx_hash,
            satoshis=satoshis_to_send,
            conf_num=0), sent_btc_obj, api_call, None

    def get_new_receiving_address(self, set_as_merchant_address=False):
        """
        Generates a new receiving address
        """
        label = urllib.quote('CoinSafe Address %s' % now().strftime("%Y-%m-%d %H.%M.%S"))

        BASE_URL = 'https://blockchain.info/merchant/%s/new_address?password=%s&label=%s'
        ADDRESS_URL = BASE_URL % (self.username, urllib.quote(self.main_password), label)

        if self.second_password:
            ADDRESS_URL += '&second_password=%s' % urllib.quote(self.second_password)

        r = requests.get(url=ADDRESS_URL)

        # Log the API call
        api_call = APICall.objects.create(
            api_name=APICall.BLOCKCHAIN_WALLET_NEW_ADDRESS,
            url_hit=ADDRESS_URL,
            response_code=r.status_code,
            post_params=None,
            api_results=r.content,
            merchant=self.merchant,
            credential=self)

        self.handle_status_code(r.status_code)

        resp_json = json.loads(r.content)

        address = resp_json['address']

        msg = '%s is not a valid bitcoin address' % address
        assert is_valid_btc_address(address), msg

        BaseAddressFromCredential.objects.create(
                credential=self,
                b58_address=address,
                retired_at=None)

        if set_as_merchant_address:
            self.merchant.set_destination_address(dest_address=address,
                    credential_used=self)

        return address

    def get_best_receiving_address(self, set_as_merchant_address=False):
        " Get a new receiving address "
        return self.get_new_receiving_address(set_as_merchant_address=set_as_merchant_address)

    @classmethod
    def create_wallet_credential(cls, user_password, merchant, user_email=None):
        """
        Create a wallet object and return its (newly created) bitcoin address
        """
        BASE_URL = 'https://blockchain.info/api/v2/create_wallet'
        label = 'CoinSafe Address %s' % now().strftime("%Y%m%d %H%M%S")

        post_params = {
                'password': user_password,
                'api_code': BCI_SECRET_KEY,
                'label': label,
                }

        if user_email:
            post_params['email'] = user_email

        r = requests.post(BASE_URL, data=post_params)

        # Log the API call
        APICall.objects.create(
            api_name=APICall.BLOCKCHAIN_CREATE_WALLET,
            url_hit=BASE_URL,
            response_code=r.status_code,
            post_params=post_params,
            api_results=r.content,
            merchant=merchant,
            )

        resp_json = json.loads(r.content)

        guid = resp_json['guid']
        btc_address = resp_json['address']

        msg = '%s is not a valid bitcoin address' % btc_address
        assert is_valid_btc_address(btc_address), msg

        cls.objects.create(
                merchant=merchant,
                username=guid,
                main_password=user_password,
                second_password=None)

        return btc_address


class BCISentBTC(BaseSentBTC):
    " No new model fields "

    def __str__(self):
        return '%s: %s' % (self.id, self.txn_hash)
