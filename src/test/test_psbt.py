import binascii
import base64
import json
import os
import unittest
from util import *

class PSBTTests(unittest.TestCase):

    def test_serialization(self):
        """Testing serialization and deserialization"""
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data/psbt.json')) as f:
            d = json.load(f)
            invalids = d['invalid']
            valids = d['valid']
            creators = d['creator']
            signers = d['signer']
            combiners = d['combiner']
            finalizers = d['finalizer']
            extractors = d['extractor']

        for invalid in invalids:
            self.assertEqual(WALLY_EINVAL, wally_psbt_from_base64(invalid.encode('utf-8'), pointer(wally_psbt())))

        for valid in valids:
            psbt = pointer(wally_psbt())
            self.assertEqual(WALLY_OK, wally_psbt_from_base64(valid.encode('utf-8'), psbt))
            ret, reser = wally_psbt_to_base64(psbt)
            self.assertEqual(WALLY_OK, ret)
            self.assertEqual(valid, reser)

        for creator in creators:
            psbt = pointer(wally_psbt())
            self.assertEqual(WALLY_OK, wally_psbt_init_alloc(2, 2, 0, psbt))

            tx = pointer(wally_tx())
            self.assertEqual(WALLY_OK, wally_tx_init_alloc(2, 0, 2, 2, tx))
            for txin in creator['inputs']:
                input = pointer(wally_tx_input())
                txid = binascii.unhexlify(txin['txid'])[::-1]
                self.assertEqual(WALLY_OK, wally_tx_input_init_alloc(txid, len(txid), txin['vout'], 0xffffffff, None, 0, None, input))
                self.assertEqual(WALLY_OK, wally_tx_add_input(tx, input))
            for txout in creator['outputs']:
                addr = txout['addr']
                amt = txout['amt']
                spk, spk_len = make_cbuffer('00' * (32 + 2))
                ret, written = wally_addr_segwit_to_bytes(addr.encode('utf-8'), 'bcrt'.encode('utf-8'), 0, spk, spk_len)
                self.assertEqual(WALLY_OK, ret)
                output = pointer(wally_tx_output())
                self.assertEqual(WALLY_OK, wally_tx_output_init_alloc(amt, spk, written, output))
                self.assertEqual(WALLY_OK, wally_tx_add_output(tx, output))

            self.assertEqual(WALLY_OK, wally_psbt_set_global_tx(psbt, tx))
            ret, ser = wally_psbt_to_base64(psbt)
            self.assertEqual(WALLY_OK, ret)
            self.assertEqual(creator['result'], ser)

if __name__ == '__main__':
    unittest.main()
