import sys
import os
import time
from jeb.api import IScript
from jeb.api import EngineOption
from jeb.api.ui import View
from jeb.api.dex import Dex
from jeb.api.ast import Class, Field, Method, Call, Constant, StaticField, NewArray, Assignment, InstanceField, Identifier, Definition, Block, IfStm, Predicate, New, Return, Expression, ArrayElt, WhileStm, DoWhileStm, SwitchStm, Label, Continue, Break, Goto, ForStm, TryStm
#from jeb.api.ast import *

#initial script is from http://drops.wooyun.org/mobile/6665, say thanks
class ViewElement(IScript):
    #thz are just stub proxy, used for function ptr
    def getInt(self, element):
        return element.getInt()
    def getBoolean(self, element):
        return element.getBoolean()
    def getByte(self, element):
        return element.getByte()
    def getString(self, element):
        return element.getString()

    def run(self, j):
        self.instance = j
        sig = self.instance.getUI().getView(View.Type.JAVA).getCodePosition().getSignature()
        
        #function ptr
        self.d_type_func = {
            'I' : self.getInt,
            'Z' : self.getBoolean,
            'B' : self.getByte,
            'Ljava/lang/String;' : self.getString,
            #others to be done
        }
        
        
        currentMethod = self.instance.getDecompiledMethodTree(sig)
        self.instance.print("scanning method: " + currentMethod.getSignature())
        
        #arguments
        print 'Arguments Info:'
        l_Arg = currentMethod.getParameters()
        for arg in range(len(l_Arg)):
            self.viewElement(l_Arg[arg], 1)
            
        #Body
        print 'Body Info:'
        body = currentMethod.getBody()
        self.instance.print(repr(body))
        for i in range(body.size()):
            self.viewElement(body.get(i),1)
            
    def getConstantValue(self, element):
        self_element = element
        type = element.getType()
        if str(type).find('None') != -1:
            return ('None', 'null')
        
        if type not in self.d_type_func.keys():
            return (type, 'TBD')
        return (type, self.d_type_func[type](element))

    def viewElement(self, element, depth):
        #self.instance.print("    "*depth+repr(element),)
        print "    "*depth+repr(element),  "   ",
        
        flgHit = False
        '''
        jeb.api.ast.InstanceField@54e7c1e4
            jeb.api.ast.Identifier@1bfa1457
            jeb.api.ast.Field@555cb707
            
        jeb.api.ast.InstanceField@61c3104c
            jeb.api.ast.InstanceField@52a47d1c
                jeb.api.ast.Identifier@5348bcaa
                jeb.api.ast.Field@29609bd2
            jeb.api.ast.Field@5058afc2
        '''
        if isinstance(element, InstanceField):
            flgHit = True
            iexp = element.getInstance()
            if isinstance(iexp, Identifier):
                print iexp.getName(),
            else:
                print iexp,
            print "." + element.getField().getName(),
            
        '''
        simple as it is
        '''
        if isinstance(element, Identifier):
            flgHit = True
            print element.getName(),
            
        if isinstance(element, Field):
            flgHit = True
            print element.getName(),
        
        '''
        jeb.api.ast.Method@3c8064be    
            jeb.api.ast.Definition@4bb004d1          #argument
                jeb.api.ast.Identifier@7c9a8b52     arg3
            jeb.api.ast.Definition@4103c412          #argument 
                jeb.api.ast.Identifier@7e19ed18     arg4
            jeb.api.ast.Block@35c4f886                #implementation
                jeb.api.ast.IfStm@1d2c2577
        jeb.api.ast.Call@76d6f65c
            jeb.api.ast.Method@6a58b6b9
            jeb.api.ast.Identifier@58a59ed2
            
        jeb.api.ast.Call@32f4a58f
            jeb.api.ast.Method@12a489fa
                jeb.api.ast.Definition@2f984416
                    jeb.api.ast.Identifier@2bce4560
                jeb.api.ast.Block@3c01454b
                    jeb.api.ast.Definition@a5cf068
                        jeb.api.ast.Identifier@6789adc1
        '''
        if isinstance(element, Call):
            flgHit = True
            print element.getMethod().getSignature(),
            #return
        
        '''
        jeb.api.ast.Definition@2f984416
            jeb.api.ast.Identifier@2bce4560
        '''
        if isinstance(element, Definition):
            flgHit = True
            print element.getType(), " ", element.getIdentifier().getName(),

        '''
        jeb.api.ast.Block@3c01454b
            jeb.api.ast.Definition@a5cf068
                jeb.api.ast.Identifier@6789adc1
            jeb.api.ast.IfStm@4fd7108f
                jeb.api.ast.Predicate@341e5919
        '''
        if isinstance(element, Block):
            flgHit = True
            print 'Block_size: ', element.size(), 
            
        '''
        jeb.api.ast.IfStm@49be613b    
             jeb.api.ast.Predicate@709f5c13    
                 jeb.api.ast.Predicate@2bf683ce    
                     jeb.api.ast.Identifier@5ff2ffae     arg4
                     jeb.api.ast.Constant@766ebd0    
                 jeb.api.ast.Predicate@d1350eb    
                     jeb.api.ast.InstanceField@12644a74     arg4 .length
                         jeb.api.ast.Identifier@5a23d819     arg4
                         jeb.api.ast.Field@6a2b90e6     length
                     jeb.api.ast.Constant@7d281140    
             jeb.api.ast.Block@4dafc37b     size:  1
        '''
        if isinstance(element, IfStm):
            flgHit = True
            print 'IfStm_Branch_Size: ', element.size(),
            
        if isinstance(element, Predicate):
            flgHit = True
            print element.getLeft(), ' ', element.getOperator().toString(), ' ', element.getRight(),
            
        if isinstance(element, Constant):
            flgHit = True
            ret = self.getConstantValue(element)
            print ret[0], ' ', ret[1],
            
        '''
        jeb.api.ast.New@41c68c0e    
             jeb.api.ast.Method@6bfc7631    
             jeb.api.ast.Identifier@2a124c13     arg4
             
        jeb.api.ast.New@1009e20e    
             jeb.api.ast.Method@14e3fc8e    
                 jeb.api.ast.Definition@35bc18c1     Lcom/g/g$a;   this
                     jeb.api.ast.Identifier@7931b963     this
        '''
        if isinstance(element, New):
            flgHit = True
            print element.getMethod().getSignature(),
            
        '''
        jeb.api.ast.NewArray@5f0d9273                            same_level_17 :
            jeb.api.ast.Constant@2741de4f     I   8192 
        
        jeb.api.ast.NewArray@c42d4db     [B   [jeb.api.ast.Constant@635cd9c0]   None                        same_level_17 :
             jeb.api.ast.Constant@abd2d13     I   8192                        same_level_18 :
            
        jeb.api.ast.NewArray@3bf41c45                            same_level_4 :
             jeb.api.ast.InstanceField@5a40bc83     v0 .c                        same_level_5 :
                 jeb.api.ast.Identifier@24ae0ad5     v0                        same_level_6 :
                 jeb.api.ast.Field@31640f20     c  
                 
        jeb.api.ast.NewArray@6a22e821     [B   [jeb.api.ast.InstanceField@50c18c]   None                        same_level_4 :
             jeb.api.ast.InstanceField@14ceb6c5     v0 .c                        same_level_5 :
                 jeb.api.ast.Identifier@16c04a91     v0                        same_level_6 :
                 jeb.api.ast.Field@6b5ecb88     c                        same_level_6 :
        '''
        if isinstance(element, NewArray):
            flgHit = True
            print element.getType(), ' ', element.getSizes(), ' ', element.getInitialValues(),
            
        '''
        jeb.api.ast.ArrayElt@181a541f                  same_level_11 :
             jeb.api.ast.Identifier@4b9257cd     arg8                        same_level_12 :
             jeb.api.ast.Identifier@78c60f5e     arg9
             
        jeb.api.ast.ArrayElt@7ec8054a                   same_level_15 :
             jeb.api.ast.StaticField@2fc4da0a     TBD, not dealed with                        same_level_16 :
                 jeb.api.ast.Field@39d70bcf     u                        same_level_17 :
             jeb.api.ast.Identifier@69789c71     v4 
             
        jeb.api.ast.ArrayElt@6e19ace1     TBD, not dealed with                        same_level_2 :
             jeb.api.ast.Identifier@609e6b3f     v0                        same_level_3 :
             jeb.api.ast.Constant@13a87ca1     I   1
        '''
        if isinstance(element, ArrayElt):
            flgHit = True
            ary = element.getArray()
            index = element.getIndex()
            if isinstance(ary, Identifier) and isinstance(index, Identifier):
                #seem not necessary, bkz the two Identifier will just follow 
                print ary.getName() + '[' + index.getName() + ']',
            elif isinstance(ary, Identifier) and isinstance(index, Constant):
                print ary.getName() + '[' + index.getInt() + ']',
            else:
                flgHit = False
                
        '''
        jeb.api.ast.SwitchStm@7b908296     TBD, not dealed with                        same_level_8 :
             jeb.api.ast.InstanceField@568f1fda     arg11 .f                        same_level_9 :
                 jeb.api.ast.Identifier@5197f338     arg11                        same_level_10 :
                 jeb.api.ast.Field@3a59663d     f                        same_level_10 :
             jeb.api.ast.Block@4522d7d2     Block_size:  1                        same_level_9 :
                 jeb.api.ast.Goto@7404b707     TBD, not dealed with                        same_level_10 :
                     jeb.api.ast.Label@48479168     TBD, not dealed with                        same_level_11 :
             jeb.api.ast.Block@192abbe8     Block_size:  1                        same_level_9 :
                 jeb.api.ast.Goto@658d813d     TBD, not dealed with                        same_level_10 :
                     jeb.api.ast.Label@2db71e1c     TBD, not dealed with 
        '''
        if isinstance(element, SwitchStm):
            flgHit = True
            print element.getSwitchedExpression(), element.getCaseKeys(), element.getCaseBodies(),
        
        '''
        jeb.api.ast.Label@6fb1e64a 
        '''
        if isinstance(element, Label):
            flgHit = True
            print element.getName(),
               
        '''
        jeb.api.ast.WhileStm@144043c1                          same_level_8 :
             jeb.api.ast.Predicate@526a7ceb     jeb.api.ast.Identifier@270c471f   <   jeb.api.ast.Identifier@70995152                        same_level_9 :
                 jeb.api.ast.Identifier@66d14acb     v0                        same_level_10 :
                 jeb.api.ast.Identifier@67ddefde     arg10                        same_level_10 :
             jeb.api.ast.Block@222c7885     Block_size:  5
        '''
        if isinstance(element, WhileStm) :#or isinstance(element, DoWhileStm):
            #almost the same with IfStm
            flgHit = True
            pass
        
        '''
        jeb.api.ast.ForStm@124eae6d     TBD, not dealed with                        same_level_1 :
             jeb.api.ast.Assignment@7f50016b                            same_level_2 :
                 jeb.api.ast.Identifier@79e0dcf8     v1                        same_level_3 :
                 jeb.api.ast.Constant@7102f1f0     I   0                        same_level_3 :
             jeb.api.ast.Predicate@16d8047b     jeb.api.ast.Identifier@697c1492   <   jeb.api.ast.Call@2f138d7c   
        '''
        if isinstance(element, ForStm):
            flgHit = True
            print element.getInitializer(), element.getPredicate(), element.getPostStatement(), element.getBody(),
            
        '''
        jeb.api.ast.ArrayElt@6fd54971     TBD, not dealed with                        same_level_15 :
             jeb.api.ast.Identifier@5c4911c1     buffer                        same_level_16 :
             jeb.api.ast.Expression@7fef6e86                            same_level_16 :
                 jeb.api.ast.Identifier@44c2e19e     v5                        same_level_17 :
                 jeb.api.ast.Identifier@119a6b6     v1 
        '''
        if isinstance(element, Expression):
            flgHit = True
            print element.getLeft(), ' ', element.getOperator().toString(), ' ', element.getRight(),
            
        '''
        jeb.api.ast.TryStm@5da16155     TBD, not dealed with                        same_level_8 :
             jeb.api.ast.Block@2c3934c0     Block_size:  4                        same_level_9 :
                 jeb.api.ast.Assignment@43ea308d                            same_level_10 :
                     jeb.api.ast.Definition@708c4d81     I   v4 
        '''
        if isinstance(element, TryStm):
            flgHit = True
            count = element.getCatchCount()
            print element.getTryBody(), ' catch count: ' + str(count) + ' [',
            for i in range(count):
                print element.getCatchType(i), ' ', element.getCatchIdentifier(i).getName(),
            print ']',
            
            

        #know those not dealed with
        if isinstance(element, Assignment) or isinstance(element, Method) or isinstance(element, Return) or isinstance(element, StaticField) or isinstance(element, Continue) or isinstance(element, Break) or isinstance(element, Goto):
            flgHit = True
            pass
        if not flgHit:
            print 'TBD, not dealed with',
        
        #to know the same level relationship
        print '                       same_level_%d :'%depth,
        self.instance.print("")
        
        for sub in element.getSubElements():
            self.viewElement(sub, depth+1)