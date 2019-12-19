'''
CSC267A Project
lift rule version2
Jiachen Zhong
Dec 12, 2018
Python 3+
'''
from itertools import combinations
import copy
import sys
sys.setrecursionlimit(100000)# set the max recursion depth
class lift_rule:

    def __init__(self, database):
        self.db = database # used for database accesses

    def ground_prob(self,table,args):
        '''
        Get the the probability of single grounded atom
        ! not completed yet
        ! need to get data from database
        args:
            table, name of table
            arge, record's attributes
        return:
            float between 0 and 1, probability of a single atom 
        '''
        return self.db.selectByArgs(table, args)

    def get_vars_DB(self,q,s):
        '''
        get all possible variables of a separator from multiple table in DB
        args:
            q, query which only contain single CNF here 
            s, separator
        return:
            list, all possible grounding values related to separator
        '''
        positions = []
        cnf = q[0]
        for atom in cnf:
            for i in range(len(atom[1])):
                # if find the separator at some location in the query, then add that position
                # to the position list
                if atom[1][i] == s:
                    positions.append((atom[0], i+1))
        return self.db.getAllPossibleValues(positions)

    def PL_interface(self,pq):
        '''
        Transfer the query from parser to the format suitable to lift_rule. Must be applied before input query from parser.
        args:
            pq, query from parser
        return:
            list, suitable format of query for lifting
        '''
        new_q=[]
        vars_num=[]
        for i in range(len(pq)):
            tmp_cnf=[]
            tmp_vars_num=set()
            for j in range(len(pq[i])):
                tmp_vars_num=tmp_vars_num.union(set(pq[i][j][1]))
                tmp_atom=[]
                tmp_atom.append(pq[i][j][0])
                tmp_atom.append(pq[i][j][1])
                tmp_s=[]
                for z in range(len(pq[i][j][1])):
                    tmp_s.append('#')
                tmp_atom.append(tmp_s)
                tmp_cnf.append(tmp_atom)
            vars_num.append(tmp_vars_num)
            new_q.append(tmp_cnf)
        ct=0
        # for i in range(len(vars_num)):
        #     while len(vars_num[i])!=0:
        #         tmp_var=vars_num[i].pop()
        #         for j in range(len(new_q[i])):
        #             for z in range(len(new_q[i][j][1])):
        #                 if new_q[i][j][1][z]==tmp_var:
        #                     new_q[i][j][1][z]='!a'+str(ct)
        #         ct=ct+1
        return new_q

    def substitution(self,q,var,con):
        '''
        substitute the constant into variable postion.
        args:
            q
            var, variable
            con, constant
        return:
            q, the query after substitute
        
        example:
        q: [[ ['S', ['a','b'],['#','#'] ],['T', ['b'],['#'] ] ]]
        var: 'b'
        con: 'amy'
        return: [[ ['S', ['a','#'],['#','amy'] ],['T', ['#'],['amy'] ] ]]
        '''
        for z in range(len(q)): 
            for i in range(len(q[z])):
                for j in range(len(q[z][i][1])):
                    if q[z][i][1][j]==var:
                        q[z][i][1][j]='#'
                        q[z][i][2][j]=con
        return q

    def check_separator(self,q):
        '''
        get the separator from query. If no separator, return empty list
        args:
            q, query which only contain single CNF here 
        return:
            list, list of separator(s). If no separator, return empty list
        example:
        q: [[ ['S', ['a','b'],['#','#'] ],['T', ['b'],['#'] ] ]]
        return: [a]
        '''
        vars_sets=[]
        for i in range(len(q[0])):
            tmp_vars_set=set()
            for j in range(len(q[0][i][1])):
                if q[0][i][1][j]!='#':
                    tmp_vars_set.add(q[0][i][1][j])
            vars_sets.append(tmp_vars_set)
        seperators=vars_sets[0]
        for i in range(1,len(vars_sets)):
            seperators=seperators.intersection(vars_sets[i])
        return list(seperators)

    def check_indpt_CQ(self,q):
        '''
        check the indpt atoms in the CNF query. If two atoms has same variable or has same relation, the two atoms are dependent
        args:
            q, query which only contain single CNF here 
        return:
            list1, list of independent atoms. If no indpt atoms, return empty list
            list2, list of dependent atoms. If no dpt atoms, return empty list
        example:
        q: [[ ['S', ['a','b'],['#','#'] ],['T', ['b'],['#'] ] ]]
        return: [], [['S', ['a','b'],['#','#'] ],['T', ['b'],['#'] ]]
        '''
        if len(q[0])==1:
            return [],q[0]
        vars_sets=[]
        for i in range(len(q[0])):
            tmp_vars_set=set()
            for j in range(len(q[0][i][1])):
                if q[0][i][1][j]!='#':
                    tmp_vars_set.add(q[0][i][1][j])
            vars_sets.append(tmp_vars_set)
        indpts=[]
        dpts=[]
        for i in range(len(vars_sets)):
            curr_q=vars_sets[i]
            indpts.append(q[0][i])
            for j in range(len(vars_sets)):
                if i==j:
                    continue
                if (not curr_q.isdisjoint(vars_sets[j])) or q[0][i][0]==q[0][j][0]:
                    indpts.pop()
                    dpts.append(q[0][i])
                    break
        return indpts,dpts

    def is_gatom(self,q):
        '''
        check the if the input query only contains grounded atom
        args:
            q
        return:
            boolean, True if query only contains grounded atom, False otherwise
        example:
        q: [[ ['S', ['#','#'],['a','b']] ]]
        return: True
        '''
        con1=(len(q)==1)
        con2=(len(q[0])==1)
        con3=True
        for i in range(len(q[0][0][1])):
            if q[0][0][1][i]!='#':
                con3=False
                break
        return (con1 and con2 and con3)



    def check_indpt_UCQ(self,q):
        '''
        check the if the input query has indpt UCQs. If two atoms has same relation, the two atoms are dependent
        args:
            q, query
        return:
            list1, list of independent UCQs. If no indpt atoms, return empty list
            list2, list of dependent UCQs. If no dpt atoms, return empty list
        '''
        optset_list=[]
        for i in range(len(q)):
            tmp_set=set()
            for j in range(len(q[i])):
                tmp_set.add(q[i][j][0])
            optset_list.append(tmp_set)
        indpts=[]
        dpts=[]    
        for i in range(len(optset_list)):
            curr_q=optset_list[i]
            indpts.append(q[i])
            for j in range(len(optset_list)):
                if j==i:
                    continue
                if (not curr_q.isdisjoint(optset_list[j])):
                    indpts.pop()
                    dpts.append(q[i])
                    break
        return indpts,dpts


    def check_hiech(self,q):
        '''
        check the if the input is Hierarchical if the query is not self-join and is hierarchical return True, otherwise return False.
        args:
            q,  query which only contain single CNF here 
        return:
            boolean, if Hierarchical return Ture; otherwise False
        '''
        Rs_set=set()
        setdict={}
        for i in range(len(q)):
            for j in range(len(q[i])):
                tmp_opt=q[i][j]
                tmp_rlat=tmp_opt[0]
                if tmp_rlat in Rs_set:
                    return True
                else:
                    Rs_set.add(tmp_rlat) 
                    for z in range(len(tmp_opt[1])):
                        tmp_var=tmp_opt[1][z]
                        if tmp_var=='#':
                            continue
                        if tmp_var in setdict:
                            setdict[tmp_var].add(tmp_rlat)
                        else:
                            setdict[tmp_var]={tmp_rlat}
        setlist=[]
        for key,val in setdict.items():
            setlist.append(val)
        for i in range(len(setlist)):
            for j in range(i+1,len(setlist)):
                if not (setlist[i].issubset(setlist[j]) or setlist[j].issubset(setlist[i]) or (setlist[i].isdisjoint(setlist[j]))):
                    return False
        return True



    def inclu_div_groups(self,q):
        '''
        divide the CNF into groups for Inclusion operation 
        args:
            q,  query which only contain single CNF here 
        return:
            list, list of indexs of group of CNF; e.g. [[0,1],[2,3],[4,5]
        '''
        vars_dict={}
        for i in range(len(q[0])):
            for j in range(len(q[0][i][1])):
                if q[0][i][1][j]=='#':
                    continue
                if q[0][i][1][j] in vars_dict:
                    vars_dict[q[0][i][1][j]].add(i)
                else:
                    vars_dict[q[0][i][1][j]]={i}
        vars_sets=[]
        for key,val in vars_dict.items():
            vars_sets.append(val)
        new_sets=[]
        for i in range(len(vars_sets)):
            new_sets.append(list(vars_sets[i]))
            for j in range(len(vars_sets)):
                if i==j:
                    continue
                if vars_sets[i].issubset(vars_sets[j]) and len(vars_sets[j].difference(vars_sets[i]))!=0:
                    new_sets.pop()
        return new_sets

    def is_incluUCQ_transferable(self,q):
        '''
        check if the UCQ is transferable for Inclusion operation
        args:
            q
        return:
            boolean, True if transferable, False otherwise
        '''
        UCQ_Rs=[]
        UCQ_Rs_sets=[]
        first_con=False # is all operations of every groups not in common; if True, every groups not in common, otherwise False. 
        for i in range(len(q)):
            CNF_Rs=set()
            CNF_sets=set()
            for j in range(len(q[i])):
                CNF_Rs.add(q[i][j][0])
                CNF_sets.add(q[i][j][0])
            UCQ_Rs.append(CNF_Rs)
            UCQ_Rs_sets.append(CNF_sets)
        for i in range(len(UCQ_Rs)-1):
            if not (len(UCQ_Rs[i])==len(UCQ_Rs[i+1]) and len(UCQ_Rs[i].intersection(UCQ_Rs[i+1]))==len(UCQ_Rs[i])):
                first_con=True
                break
        intersect_part=UCQ_Rs_sets[0]
        for i in range(1,len(UCQ_Rs_sets)):
            intersect_part=intersect_part.intersection(UCQ_Rs_sets[i])
        second_con=(len(intersect_part)!=0) # is every groups has common opeartions; if True, has the common operator, otherwise False. 
        return first_con,second_con

    def transfer_incluUCQ(self,q):
        '''
        transfer the UCQ for inclusion operation
        args:
            q
        return:
            list1, common atoms
            list2, uncommon atoms
        example:
            R(),P()||R(),Q() -> list1:R()  list2:P(),Q()
        '''
        tmp_sets=[]
        for i in range(len(q)):
            tmp_comr=set()
            for j in range(len(q[i])):
                tmp_comr.add(q[i][j][0])
            tmp_sets.append(tmp_comr)
        common_r=tmp_sets[0]
        for i in range(1,len(tmp_sets)):
            common_r=common_r.intersection(tmp_sets[i])
        tmp_com_atoms=[] 
        ncom_atoms=[]

        for i in range(len(q)):
            for j in range(len(q[i])):
                if q[i][j][0] in common_r:
                    tmp_com_atoms.append(q[i][j])
                else:
                    ncom_atoms.append(q[i][j])
        com_atoms=[]
        comrlist=list(common_r)
        for i in range(len(comrlist)):
            tmp_list=[]
            for j in range(len(tmp_com_atoms)):
                if tmp_com_atoms[j][0]==comrlist[i]:
                    tmp_list.append(tmp_com_atoms[j])
            com_atoms.append(tmp_list)
        ct=0
        for i in range(len(com_atoms)):
            for j in range(len(com_atoms[i][0][1])):
                for z in range(len(com_atoms[i])):
                    curr_att=com_atoms[i][z][1][j]
                    com_atoms[i][z][1][j]='!b'+str(ct)
                    for k in range(len(com_atoms)):
                        if k==i:
                            continue
                        for t in range(len(com_atoms[k])):
                            for u in range(len(com_atoms[k][t][1])):
                                if com_atoms[k][t][1][u]==curr_att:
                                    com_atoms[k][t][1][u]='!b'+str(ct)
                    for k in range(len(ncom_atoms)):
                        for t in range(len(ncom_atoms[k][1])):
                            if ncom_atoms[k][1][t]==curr_att:
                                ncom_atoms[k][1][t]='!b'+str(ct)
                ct=ct+1
        for i in range(len(com_atoms)):
            tmp_catom=com_atoms.pop()
            com_atoms.append(tmp_catom[0])
        return com_atoms,ncom_atoms

    def inclu_find_seps(self,outs,ins):
        '''
        find the separator in common atoms(outs) and uncommon atoms(ins)
        args:
            outs, list of common atoms
            ins,  list of uncommon atoms
        return:
            list, list of separators
        '''
        outs_set=set(outs[0][1])
        for i in range(1,len(outs)):
            outs_set=outs_set.intersection(set(outs[i][1]))
        for i in range(len(ins)):
            outs_set=outs_set.intersection(set(ins[i][1]))
        return list(outs_set)

    def inclu_trans_ins2UCQ(self,ins):
        '''
        transfer the common atoms list into UCQ format
        args:
            ins,  list of uncommon atoms
        return:
            list, UCQ format of uncommon atoms list
        '''
        result=[]
        for i in range(len(ins)):
            result.append([ins[i]])
        return result

    def is_only1R_CNF(self,q):
        '''
        if there only one relation(operation) in the CNF
        args:
            q,  query which only contain single CNF here 
        return:
            boolean, True if the CNF only has one operation, False otherwise 
        '''
        uniq_set=set()
        for i in range(len(q[0])):
            uniq_set.add(q[0][i][0])
        return (len(uniq_set)==1)


    def elim_UCQrepeat(self,q):
        '''
        eliminate the repeat CQ(CNF), which has no repeat atom, in a UCQ. 
        args:
            q, query
        return:
            list, a query after eliminating repeat CQ
            input: [[['Q',['x1'],['#']]],[['Q',['x1'],['#']]],[['Q',['x1'],['#']]] ]
            return: [[['Q',['x1'],['#']]]]
        '''
        if len(q)<=1:
            return q
        UCQ_sets=[]
        for i in range(len(q)):
            tmp_CNF=set()
            for j in range(len(q[i])):
                tmp_atom=q[i][j][0]
                for z in range(len(q[i][j][1])):
                    tmp_atom=tmp_atom+q[i][j][1][z]
                tmp_CNF.add(tmp_atom)
            UCQ_sets.append(tmp_CNF)
        new_q_ids=[]
        for i in range(len(UCQ_sets)):
            curr_CNF=UCQ_sets[i]
            new_q_ids.append(i)
            for j in range(len(UCQ_sets)):
                if i==j:
                    continue
                if len(curr_CNF)==len(UCQ_sets[j]) and len(curr_CNF.intersection(UCQ_sets[j]))==len(curr_CNF):
                    if j in new_q_ids:
                        new_q_ids.pop()
        new_q=[]
        for i in range(len(new_q_ids)):
            new_q.append(q[new_q_ids[i]])
        return new_q

    def elim_CNFrepeat(self,q):
        '''
        eliminate the repeat atoms in each CNF Query 
        args:
            q, query
        return:
            list, a query after eliminating repeat atoms in every CQ 
        example:
            input: [[['R',['x1','y1'],['#','#']],['Q',['x1'],['#']],['Q',['x1'],['#']],['P',['x1'],['#']]]
            return: [[['R',['x1','y1'],['#','#']],['Q',['x1'],['#']]]]
        '''
        new_q=[]
        for i in range(len(q)):
            CNF_set=set()
            new_CNF=[]
            for j in range(len(q[i])):
                tmp_atom=q[i][j][0]
                for z in range(len(q[i][j][1])):
                    tmp_atom=tmp_atom+q[i][j][1][z]
                if tmp_atom not in CNF_set:
                    new_CNF.append(q[i][j])
                    CNF_set.add(tmp_atom)
            new_q.append(new_CNF)
        return new_q

    def elim_CNFreddcy(self,q):
        '''
        eliminate the redundant atoms in each CNF 
        args:
            q, query
        return:
            list, a query after eliminating repeat atoms in every CQ
        example:
            input: [[['R',['x1','y1'],['#','#']],['Q',['x1'],['#']],['Q',['x2'],['#']],['P',['x3'],['#']]]
            return: [[['R',['x1','y1'],['#','#']],['Q',['x1'],['#']]]]
        '''
        new_q=[]
        Rs_list=[]
        for i in range(len(q)):
            Rs_dict={}
            for j in range(len(q[i])):
                if q[i][j][0] not in Rs_dict:
                    Rs_dict[q[i][j][0]]=set()
                for z in range(len(q[i][j][1])):
                    Rs_dict[q[i][j][0]].add(q[i][j][1][z])
            Rs_list.append(Rs_dict)
        for i in range(len(q)):
            new_set=set()
            new_CNF=[]
            for j in range(len(q[i])):
                curr_R=q[i][j][0]
                is_R_in_other=False
                for z in range(len(q[i][j][1])):
                    curr_Rs_var=q[i][j][1][z]
                    for key,val in Rs_list[i].items():
                        if key==curr_R:
                            continue
                        if curr_Rs_var in val:
                            is_R_in_other=is_R_in_other or True
                            break
                if is_R_in_other:
                    new_set.add(curr_R)
                    new_CNF.append(q[i][j])
            for j in range(len(q[i])):
                curr_R=q[i][j][0]
                if curr_R not in new_set:
                    new_set.add(curr_R)
                    new_CNF.append(q[i][j])
            new_q.append(new_CNF)
        return new_q

    def find_UCQ_seps(self,q):
        '''
        find the separators in a query 
        args:
            q, query
        return:
            list, list of separators
        '''
        UCQ_asets=[]
        for i in range(len(q)):
            for j in range(len(q[i])):
                atom_set=set()
                for z in range(len(q[i][j][1])):
                    if q[i][j][1][z]!='#':
                        atom_set.add(q[i][j][1][z])
                UCQ_asets.append(atom_set)
        sep_set=UCQ_asets[0]
        for i in range(1,len(UCQ_asets)):
            sep_set=sep_set.intersection(UCQ_asets[i])
        return list(sep_set)


    def lift(self,query):
        '''
        0. eliminate repeat and redundant atoms in query 
        1. base of recursion
        2. Decomp Disjunction in UCQ
        3. Decomp Exi Quantifier in UCQ
        4. Exclusion in UCQ
        5. Decomp Conjunction in CNF
        6. Decomp Exi Quantifier in CNF
        7. Inclusion in CNF
        8. return fail
        '''
        query=self.elim_CNFrepeat(query) # eliminate repeat atoms in CNF
        query=self.elim_UCQrepeat(query) # eliminate repeat atoms in UCQ 
        query=self.elim_CNFreddcy(query) # eliminate redundant atoms in CNF
        if len(query)==0 :
            # No query case
            return 0

        #Base of recursion; if it is a grounded atom or not
        if self.is_gatom(query) :
            return self.ground_prob(query[0][0][0],query[0][0][2])
        #Decomp Disjunction
        UCQ_indpts,UCQ_dpts=self.check_indpt_UCQ(query)
        if len(query)>1 and len(UCQ_indpts)>0:
            indpts_prdt=1
            for i in range(len(UCQ_indpts)):
                tmp_lift=self.lift([UCQ_indpts[i]])
                if tmp_lift<0:
                    return -1.0
                indpts_prdt=indpts_prdt*(1-tmp_lift)
            tmp_lift=self.lift(UCQ_dpts)
            if tmp_lift<0:
                return -1.0
            return 1-indpts_prdt*(1-tmp_lift)
        
        #Decomp Exi Quantifier in UCQ
        # replace only one separator per time
        UCQ_seps=self.find_UCQ_seps(query)
        if  len(query)>1 and len(UCQ_seps)>0:
            psib_vars=self.get_vars_DB(query,UCQ_seps[0])
            prdt=1
            for i in range(len(psib_vars)):
                tmp_lift=self.lift(self.substitution(copy.deepcopy(query),UCQ_seps[0],psib_vars[i]))
                if tmp_lift<0:
                    return -1.0
                prdt=prdt*(1-tmp_lift)
            return 1-prdt

        #Exclusion    
        # No cancellation here, if there is a part which is not liftable, the whole query is unliftable
        if len(query)>1:
            E_ids=[i for i in range(len(query))]
            E_result=0
            for i in range(len(query)):
                tmp_ids=list(combinations(E_ids,i+1))
                for j in range(len(tmp_ids)):
                    tmp_comb=[]
                    for z in range(len(tmp_ids[j])):
                        tmp_comb=tmp_comb+query[tmp_ids[j][z]]
                    tmp_lift=self.lift([tmp_comb])
                    if tmp_lift<0:
                        return -1.0
                    E_result=E_result+(pow(-1,i)*tmp_lift)
            return E_result
        
        #Decomp Conjunction
        CQ_indpts,CQ_dpts=self.check_indpt_CQ(query)
        if len(CQ_indpts)!=0 and len(query)==1:
            prdt=1
            for i in range(len(CQ_indpts)):
                tmp_lift=self.lift([[CQ_indpts[i]]])
                if tmp_lift<0:
                    return -1.0
                prdt=prdt*tmp_lift
            if len(CQ_dpts)==0:
                return prdt
            tmp_lift=self.lift([CQ_dpts])
            if tmp_lift<0:
                return -1.0
            return prdt*tmp_lift
        
        # Decomp Exi Quantifier in CNF
        # replace only one sperator per time
        sprts=self.check_separator(query)
        if len(sprts)!=0 and len(query)==1:
            psib_vars=self.get_vars_DB(query,sprts[0])
            prdt=1
            for i in range(len(psib_vars)):
                tmp_lift=self.lift(self.substitution(copy.deepcopy(query),sprts[0],psib_vars[i]))
                if tmp_lift<0:
                    return -1.0
                prdt=prdt*(1-tmp_lift)
            return 1-prdt
        
        #Inclusion for CNF
        if self.is_only1R_CNF(query):
            tmp_lift=self.lift([[query[0][0]]])
            if tmp_lift<0:
                return -1.0
            return tmp_lift
        if self.check_hiech(copy.deepcopy(query)) and len(query)==1:
            I_result=0
            # divide query into disjoint CNF groups according to variables
            I_ids=self.inclu_div_groups(copy.deepcopy(query))
            IS_ids=[i for i in range(len(I_ids))]
            # apply inclusion formula on all combinations of groups of all lengths
            for i in range(len(IS_ids)):
                tmpS_ids=list(combinations(IS_ids,i+1))
                for j in range(len(tmpS_ids)):
                    tmp_UCQ=[]
                    for z in range(len(tmpS_ids[j])):
                        tmpI_id=I_ids[tmpS_ids[j][z]]
                        tmp_CNF=[]
                        for k in range(len(tmpI_id)):
                            tmp_CNF.append(copy.deepcopy(query[0][tmpI_id[k]]))
                        tmp_UCQ.append(tmp_CNF)
                    # current combination has only one group in it
                    if i<1:
                        tmp_lift=self.lift(tmp_UCQ) 
                        if tmp_lift<0:
                            return -1.0
                        I_result=I_result+tmp_lift
                    else:
                        # if the combination cannot be transformed, then it can be two cases
                        # 1. current combination is unliftable: return unliftable
                        # 2. each group has the exact same set of parameters: lifting any group is sufficient
                        trsf_1stco,trsf_2ndco=self.is_incluUCQ_transferable(tmp_UCQ)
                        if not (trsf_1stco and trsf_2ndco):
                            if trsf_1stco:
                                return -1.0
                            else:
                                tmp_lift=self.lift([tmp_UCQ[0]])
                                if tmp_lift<0:
                                    return -1.0
                                I_result=I_result+pow(-1,i)*tmp_lift   
                        # if there are common parameters, then simplify the formula and calculate the result
                        else:
                            outs,ins =self.transfer_incluUCQ(tmp_UCQ)
                            inclu_seps=self.inclu_find_seps(outs,ins)
                            suted_outs=[]
                            suted_ins=[]
                            if len(inclu_seps)<=0:
                                return -1.0
                            for z in range(len(inclu_seps)):
                                dom_cnf=[]
                                for k in range(len(outs)):
                                    dom_cnf.append(outs[k])
                                for k in range(len(ins)):
                                    dom_cnf.append(ins[k])
                                psib_vars=self.get_vars_DB([dom_cnf],inclu_seps[z])
                                for k in range(len(psib_vars)):
                                    suted_outs.append(self.substitution([copy.deepcopy(outs)],inclu_seps[z],psib_vars[k]).pop())
                                    suted_ins.append(self.substitution([copy.deepcopy(ins)],inclu_seps[z],psib_vars[k]).pop())
                            tmp_prdt=1
                            if len(suted_outs)<=0:
                                return -1.0
                            for z in range(len(suted_outs)):
                                tmp_lift1=self.lift(self.inclu_trans_ins2UCQ(suted_ins[z]))
                                if tmp_lift1<0:
                                    return -1.0
                                tmp_lift2=self.lift([suted_outs[z]])
                                if tmp_lift2<0:
                                    return -1.0
                                tmp_prdt=tmp_prdt*(1-tmp_lift1*tmp_lift2)
                            I_result=I_result+pow(-1,i)*(1-tmp_prdt)          
            return I_result
        # not liftable
        return -1.0

