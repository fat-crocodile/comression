import sys
sys.path.insert(0, '../src')

from bitstream import InputStream
import deflate_decoder as decoder


data = '\xcd\xd0A\n\xc20\x10\x05\xd0}N\xf1\x0f \xdeAw\xee\xdd\xb8\x9c\xda\x9f\x1a\x1a\'0i)\xb9\xbdIAPW\x8a\x08B6\t3\x93\xf7g\x1f\xe5<v\xc1z\xe4\xa0C=\x08\x8a\xe9B\xf4\x94\x1e\xc9C\xc3p\x99\xdcQF\xb6\xe7Lt\x96F*\x96Z\x9b!\xda#R\xac\xf6$\xf8X\xdc.F\x944\x1bb\xf0t\xa74c\xa1\x11Ic\xc1"aj?\xf8duV\xc8\xb8\xa6+uj\xadb!\xd3\xb9}\xd3\xe0#N\x9e\xb5qX\xf8\xa2\xc9\xa4\x93\'MyW\xd3\x11\xdex\xf7\xac\x9c\x9am\x83\xa7\xab;h-m\xb6\xd8L\r\xb7B\xc5j\x825\xc7j\xdd>N\xf9\x9b\x1d\x7f\x9d\xe9+\xc3O\xcbo'


#data = 'K\xcaIL\xceN\xca,JQ(\xce\xccK\x07"\x85\xcc<\x85\x92\x8cT\x85\x94\xd4\xc4\x14\x85\xfc4\x85\xbc\xcc\xf4\x8c\x12\xae\x92\xc4\xecT\x90Xq\xaaBRQ~vj\x9eB9Pu\xb1Bb^\x8aBNjb\x11Ps\xbeBZN%WbN\x8eBe~i\x91BNfZ*\x17\x90\xa9P\x9eZ\x94\xaa\x90\x9f\x97S\xa9P\x9e\x98Y\x02\xb20-\xbf\x08htf\xb1Bn~nj^\tHWbQfq*\x00'

#data = 'K\xcaIL\xceN\xca,JQ(\xce\xccK\x07"\x85\xcc<\x85\x92\x8cT\x85\x94\xd4\xc4\x14\x85\xfc4\x85\xbc\xcc\xf4\x8c\x12\xae\x92\xc4\xecT\x90pq\xaaBRQ~vj\x9eB9Pm\xb1Bb^\x8aBNjb\x11PO\xbeBZN%WbN\x8eBe~i\x91BNfZ*\x17\x90\xa5P\x9eZ\x94\xaa\x90\x9f\x97S\xa9P\x9e\x98Y\x02\xb2!-\xbf\x08hVf\xb1Bn~nj^\tHkbQfq*\x00'


#data = 'x\x9cK\xcaIL\xceN\xca,JQ(\xce\xccK\x07"\x85\xcc<\x85\x92\x8cT\x85\x94\xd4\xc4\x14\x85\xfc4\x85\xbc\xcc\xf4\x8c\x12\xae\x92\xc4\xecT\x90pq\xaaBRQ~vj\x9eB9Pm\xb1Bb^\x8aBNjb\x11PO\xbeBZN%WbN\x8eBe~i\x91BNfZ*\x17\x90\xa5P\x9eZ\x94\xaa\x90\x9f\x97S\xa9P\x9e\x98Y\x02\xb2!-\xbf\x08hVf\xb1Bn~nj^\tHkbQfq*\x00\xf8|2\xee'


#data = 'cdd0410ac2301005d07d4ef10f20de4177eeddb89cda9f1a1a27306929b9bd494150578a084236093393f7671fe53c76c17ae4a0433d088ae942f4941ec943c37099dc5146b6e74c7496462a965a9b21da2352acf624f858dc2e4694341b62f074a73463a1114963c122616a3ff8647556c8b8a62b756aad6221d3b97dd3e0234e9eb57158f8a2c9a493274d7957d311de78f7ac9c9a6d83a7ab3b682d6db6d84c0db742c56a8235c76add3e4ef99b1d7f9de92bc36fcb6f'.decode('hex')


#data = 'd5564d6fdb300cbdfb57b01db0da6b93263d15455d60871d76d90e3b0e43603b72acc19103494913603f7e94acd8d68793762b06cc877c5032f9483df2e9ddc5ed56f0db9cb25bc276b039c8aa615154d49910f0996db6f29be4245bc74dfe9314327988009fcbcbcb15914025e1595e13684a108775ded4e206d476b50499801cbf847eff064adeaca16e9e0987fc20895a13201ba8e8aa221c3d46daf59294b0585046e562110b529737b0cc646602ab4719a7ca06a94610eb757b199da38f25d9e39e99b384c14fada1f54bc3488f06335dd4c460610320889913b9e50cd844654a99242bc2b1041556a0ce0e6831e95bd97b891f1dd21218a488ea018ce359d4036cb6bc50e8bafca78cec65b76eb0f779a0b7c11f01ac913a3320b520c65ddcd74d65903ad5eba37322ec7255b494da62a37f4ae11e26ca595fa7e3fbd729c40d5fc60a50024f4f6a5762ed6abde2be7b55506b89c124646e51cf6c9ba984c9d00083599bb83e5c2ba8c30a0c3fef36743f9e2b8a446f137c616af0f8d86634926320bf37cfc3391da456107b1c40ff1ecd7395034bf044e7499f4fe21d01fa60d1780b0e4f6dd868ea6b40314d798464f75efe26bdd7765bd77cba15ffb3def3b9183ace547f7e803bb886f0b1ce83e737f7e938a08f299106ea75409fc2cc35fbfb5e476a5dfd93c4fe6bb2753015e14a541e512dd45ecd3a5777ce08cb513cce43efd81d88d4b1a70b76917a479d51acd7a77d413692362cbefa5853b65a13268170def0ab01bb3ce2c6ae5c8e4c3f53254da2c4c72d028df946d8bbfd65c381aa66def38cad483c8ca59e0325f5723cbdf14368af385fb772fc8e23b25d7b4f69e7085e68cc2fbcef1455c6b302af1fe23845bc9b8bc79d6d59e2084ae1fb8f20735c3e5954eb4220dcfe3ab2f38a6f0fb1d313a65b74c697337910ae1de15abbf39570496a7d2b3337005fcc7ea1d4ec7a61d1fb07e2f21271d78349bf689977f87ec88e194cb3cd8630330643021b9aac21953f3a1a64706fd09f93f2165e6f3b23cba162b13385d212ecf9ffb3e938a0eb14fb49255d543cde27ba1df7aa1db11e894dcafc1f913270271bad1f1610752f66135538a57c27aa670be04bc46e44a9daba19b2a8ba69e625be17b7edd5e30aefeb0ed0d1b113636888af739304742138983ae35013dc68fde1ea88e787a1911b1945bf01'.decode('hex')



#data = '789C05200049F64F61540100040200A200A1'.decode('hex')
#data = '789c6358000000a200a1'.decode('hex')

#data = sys.stdin.read()
#data = data[2:-4]

#data = '63580000'.decode('hex')


bs = InputStream(data)

def logger(x):
    print >> sys.stderr, x

print ''.join(decoder.decode(bs, logger))

