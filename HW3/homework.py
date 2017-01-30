# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 21:06:46 2016

@author: caixi
"""

import ply.lex, ply.yacc
from collections import deque
#import os

# List of token names.   This is always required
tokens = [
   'NOT',
   'OR',
   'AND',
   'IMPLIES',
   'CHAR',
   'LPAREN',
   'RPAREN',
   'STRING',
   'COMMA'
]

# Tokens
t_STRING   = r'[A-Z][A-Za-z]*'
t_IMPLIES  = r'=>'
t_NOT    = r'~'
t_OR   = r'\|'
t_AND   = r'&'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_CHAR = r'[a-z]'
t_COMMA = r','

# Ignored characters
t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

lexer = ply.lex.lex()

# Parsing rules
precedence = (
    ('left','IMPLIES'),
    ('left','OR'),
    ('left','AND'),
    ('right','NOT'),
    )

def p_sentence(t):
    '''sentence : atomicsentence 
    | complexsentence'''
    t[0] = t[1]
    
def p_atomic_sentence(t):
    'atomicsentence : STRING LPAREN terms RPAREN'
    #t[1] is predicate
    #t[2] contains the terms
    t[0] = ('PREDICATE', t[1], t[3])
    
def p_complex_sentence(t):
    '''complexsentence : LPAREN sentence RPAREN 
    | NOT sentence  '''
    if len(t) == 4:
        #rule 1
        t[0] = t[2]
    else:
        #rule 2
        t[0] = ('NOT', t[2])
    
def p_complex_sentence2(t):
    '''complexsentence : sentence AND sentence 
    | sentence OR sentence 
    | sentence IMPLIES sentence'''
    if t[2] == '&':
        #rule 1
        t[0] = ('AND', t[1], t[3])
    elif t[2] == '|':
        #rule 2
        t[0] = ('OR', t[1], t[3])
    else:
        #rule 3
        t[0] = ('IMPLIES', t[1], t[3])
        
def p_terms(t):
    '''terms : term 
    | term COMMA terms'''
    if len(t) == 2:
        #rule 1
        t[0] = (t[1],)
    else:
        #rule 2
        t[0] = (t[1],) + t[3]
        
def p_term(t):
    '''term : constant 
    | variable'''
    t[0] = t[1]
    
def p_constant(t):
    'constant : STRING'
    t[0] = ('CONSTANT', t[1])
    
def p_variable(t):
    'variable : CHAR'
    t[0] = ('VARIABLE', t[1])
    
# Error rule for syntax errors
def p_error(t):
    print("Syntax error in input!")    
    
parser = ply.yacc.yacc()

#----------------------DEBUGGING METHODS-----------------------------------
#For a FOL sentence, return the list of predicates
def GetAllPredicateNames(aSentence, aPredicateSet):
    if aSentence[0] == 'PREDICATE':
        aPredicateSet.add(aSentence[1])
        return
    GetAllPredicateNames(aSentence[1], aPredicateSet)
    if len(aSentence) >= 3:
        GetAllPredicateNames(aSentence[2], aPredicateSet) 
    
#For a list of predicates, find all possible models
#Each model is a dictionary mapping a predicate to True/False
def GetAllPossibleModels(aPredicates):
    modelList = []
    for i in xrange(2**len(aPredicates)):
        model = {}
        for j in xrange(len(aPredicates)):
            if i & (1 << j) != 0:
                model[aPredicates[j]] = True
            else:
                model[aPredicates[j]] = False
        modelList.append(model)
    return modelList
    
#Evaluates whether a FOL sentence is true/false given a model
def Evaluate(aSentence, aModel):
    if aSentence[0] == 'PREDICATE':
        return aModel[aSentence[1]]
    if aSentence[0] == 'NOT':
        return not Evaluate(aSentence[1], aModel)
    if aSentence[0] == 'AND':
        return Evaluate(aSentence[1], aModel) and Evaluate(aSentence[2], aModel)
    if aSentence[0] == 'OR':
        return Evaluate(aSentence[1], aModel) or Evaluate(aSentence[2], aModel)
    if aSentence[0] == 'IMPLIES':
        tmp = Evaluate(aSentence[1], aModel)
        if not tmp:
            return True
        return Evaluate(aSentence[2], aModel)
 
#Check if 2 FOL sentences are equivalent
def AreEquivalent(aSentence1, aSentence2):
    predicates1 = set()
    predicates2 = set()
    GetAllPredicateNames(aSentence1, predicates1)
    GetAllPredicateNames(aSentence2, predicates2)
    if predicates1 != predicates2:
        return False
    modelList = GetAllPossibleModels(list(predicates1))
    for model in modelList:
        result1 = Evaluate(aSentence1, model)
        result2 = Evaluate(aSentence2, model)
        if result1 != result2:
            return False
    return True
        
#Serialize FOL sentence object as string
def DumpS(aSentence):
    if aSentence[0] == 'PREDICATE':
        result = ""
        for x in aSentence[2]:
            result += x[1] + ','
        return aSentence[1] + '(' + result[:-1] + ')'
    aStr1 = DumpS(aSentence[1])
    if len(aSentence) >= 3:
        aStr2 = DumpS(aSentence[2])
    if aSentence[0] == 'NOT':
        result = '~' + '(' + aStr1 + ')'
    elif aSentence[0] == 'AND':
        result = '(' + aStr1 + ') & ' + '(' + aStr2 + ')'
    elif aSentence[0] == 'OR':
        result = '(' + aStr1 + ') | ' + '(' + aStr2 + ')'
    elif aSentence[0] == 'IMPLIES':
        result = '(' + aStr1 + ') => ' + '(' + aStr2 + ')'
    return result                
 
#Dump sentence as a tree string
def TreeDumpS(aSentence, aIndentation = ''):
    if aSentence[0] == 'PREDICATE':
        currStr = aIndentation + aSentence[1] + '('
        for i in xrange(len(aSentence[2])):
            currStr += aSentence[2][i][1] + ','
        currStr = currStr[:-1] + ')'
    else:
        currStr = aIndentation + 'OPERATOR: ' + aSentence[0] + '\n'
        for i in xrange(1, len(aSentence)):
            currStr += aIndentation + 'OPERAND' + str(i) + ':\n' + TreeDumpS(aSentence[i], aIndentation + '\t') + '\n'
    return currStr

#Dump a clause (array of predicates) into a string    
def ClauseDumpS(aClause):
    s = ''
    for predicate in aClause:
        predName = GetPredicateName(predicate)
        s += predName + '('
        terms = predicate[1][2] if predName[0] == '~' else predicate[2]
        for t in terms:
            s += t[1] + ','
        s = s[:-1] + ') | '
    return s[:-3]
#-----------------------------------------------------------------------------

def RemoveImplications(aSentence):
    #exit if reach predicate unit
    if aSentence[0] == 'PREDICATE':
        return aSentence
    newOperator = aSentence[0]
    newLeftOperand = RemoveImplications(aSentence[1])
    #if operand of current node is implies, perform implication elimination
    if aSentence[0] == 'IMPLIES':
        newOperator = 'OR'
        newLeftOperand = ('NOT', newLeftOperand)
    if len(aSentence) >= 3:
        newRightOperand = RemoveImplications(aSentence[2])
        return (newOperator, newLeftOperand, newRightOperand)
    return (newOperator, newLeftOperand)
    
def MoveNegInwards(aSentence, hasNeg = False):
    #Idea:
    #At each node, check if there is negation
    #If yes, move negation downwards using De Morgan's
    #After moving inwards, check if it results in double negation
    #If yes, remove double negation
    if aSentence[0] == 'PREDICATE':
        if hasNeg:
            return ('NOT', aSentence)
        return aSentence
    if aSentence[0] == 'NOT':
        if hasNeg:
            #double negation elmination
            return MoveNegInwards(aSentence[1], False)
        #Move negation inwards
        return MoveNegInwards(aSentence[1], True)
    #De Morgan's: ~(A | B) becomes ~A & ~B     
    if aSentence[0] == 'OR':
        opr = 'AND' if hasNeg else 'OR'
        return (opr, MoveNegInwards(aSentence[1], hasNeg), MoveNegInwards(aSentence[2], hasNeg))
    #De Morgan's: ~(A & B) becomes ~A | ~B   
    if aSentence[0] == 'AND':
        opr = 'OR' if hasNeg else 'AND'
        return (opr, MoveNegInwards(aSentence[1], hasNeg), MoveNegInwards(aSentence[2], hasNeg))
    #Implication removal is assumed to have occurred, therefore, does not
    #handle that case.
        
def DistributeOrOverAnd(aSentence):
    #MoveNegInwards should have been called,
    #therefore negation would be atomic
    if aSentence[0] == 'PREDICATE' or  aSentence[0] == 'NOT':
        return aSentence
    if aSentence[0] == 'OR':
        #All operators are binary
        #Distribute left over right if right term has AND operator
        if aSentence[2][0] == 'AND':
            newLeftOperand = DistributeOrOverAnd(('OR', aSentence[1], aSentence[2][1]))
            newRightOperand = DistributeOrOverAnd(('OR', aSentence[1], aSentence[2][2]))
            return ('AND', newLeftOperand, newRightOperand)
        #Distribute right over left if left term has AND operator
        if aSentence[1][0] == 'AND':
            newLeftOperand = DistributeOrOverAnd(('OR', aSentence[1][1], aSentence[2]))
            newRightOperand = DistributeOrOverAnd(('OR', aSentence[1][2], aSentence[2]))
            return ('AND', newLeftOperand, newRightOperand)
    return (aSentence[0], DistributeOrOverAnd(aSentence[1]), DistributeOrOverAnd(aSentence[2]))
            
def ConvertToCNF(aSentence):  
    return DistributeOrOverAnd(MoveNegInwards(RemoveImplications(aSentence)))
    
#Convert a CNF sentence as a 2D array, where each row is a clause and an
#entry in that row is a predicate.    
def ExtractClausesFromCNF(aSentence):
    def ExtractPredicatesFromClause(aClause):
        if aClause[0] != 'OR':
            return (aClause,)
        return ExtractPredicatesFromClause(aClause[1]) + ExtractPredicatesFromClause(aClause[2])
    if aSentence[0] != 'AND':
        return [ExtractPredicatesFromClause(aSentence)]
    return ExtractClausesFromCNF(aSentence[1]) + ExtractClausesFromCNF(aSentence[2])

#Get the predicate name given the predicate object, a '~' will be prefixed
#if the predicate is negated, i.e. P(x) => P, ~P(x) => ~P.
def GetPredicateName(aPredicate):
    if aPredicate[0] == 'NOT':
        predicateName = '~' + aPredicate[1][1]
    else:
        predicateName = aPredicate[1]
    return predicateName
    
#Update the predicate index aPredicateIndex based on addition of clause, 
#such that aPredicateIndex(p) = list of clauses which contain predicate with 
#name p. Note: If predicate is negated, name will be prefixed 
#with a '~', e.g. P(x) will have name P and ~P(x) will have name ~P.
def UpdatePredicateIndex(aClause, aPredicateIndex):
    for predicate in aClause:
        predicateName = GetPredicateName(predicate)
        if predicateName not in aPredicateIndex:
            aPredicateIndex[predicateName] = []
        if aClause not in aPredicateIndex[predicateName]:
            aPredicateIndex[predicateName].append(aClause)

#Unify 2 FOL clauses, aTheta is a tuple (x, y), where x is the subsitution list
# and y is whether there is failure
def Unify(aExpr1, aExpr2, aTheta = {}):
    #No need occur check since there are no function symbols and 
    #this causes predicates, which are the most atomic units, to have only 
    #constants.
    #Return if failure
    if aTheta is None:
        return None
    #Check if aExpr1 == aExpr2
    if aExpr1 == aExpr2:
        return aTheta
    #if aExpr1 is variable
    if len(aExpr1) > 0 and aExpr1[0] == 'VARIABLE':
        return UnifyVar(aExpr1, aExpr2, aTheta)
    #if aExpr2 is variable
    if len(aExpr2) > 0 and aExpr2[0] == 'VARIABLE':
        return UnifyVar(aExpr2, aExpr1, aTheta)
    if len(aExpr1) > 0 and aExpr1[0] == 'PREDICATE' and len(aExpr2) > 0 and aExpr2[0] == 'PREDICATE':
        return Unify(aExpr1[2], aExpr2[2], Unify(aExpr1[1], aExpr2[1], aTheta))
    if len(aExpr1) > 0 and aExpr1[0] == 'NOT' and len(aExpr2) > 0 and aExpr2[0] == 'NOT':
        return Unify(aExpr1[1], aExpr2[1], aTheta)
    #if aExpr1 and aExpr2 are both terms
    if len(aExpr1) > 0 and type(aExpr1[0]) is tuple and len(aExpr2) > 0 and type(aExpr2[0]) is tuple:
        return Unify(aExpr1[1:], aExpr2[1:], Unify(aExpr1[0], aExpr2[0], aTheta))
    #Return failure
    return None
    
#Helper method used by Unify to unify a variable with an expression
def UnifyVar(aVar, aExpr, aTheta):
    if aVar in aTheta:
        return Unify(aTheta[aVar], aExpr, aTheta)
    if aExpr in aTheta:
        return Unify(aVar, aTheta[aExpr], aTheta)
    aTheta = aTheta.copy() #might not need to copy
    aTheta[aVar] = aExpr
    return aTheta        

def LoadInput(aInputFile):
    with open(aInputFile, 'r') as f:
        numOfQueries = int(f.readline())
        queries = [None] * numOfQueries
        for i in xrange(numOfQueries):
            folObj = parser.parse(f.readline().strip())
            queries[i] = folObj
        numOfSentences = int(f.readline())
        kb = []
        clauses = []
        for i in xrange(numOfSentences):
            folObj = parser.parse(f.readline().strip())
            folObj = ConvertToCNF(folObj)
            #print DumpS(folObj)            
            clauses.extend(ExtractClausesFromCNF(folObj))
        for c in clauses:
            if not IsTautology(c):
                kb.append(c)
    return queries, kb
    
#Substitute aTheta into aClause
def Substitute(aClause, aTheta):
    newClause = ()
    for predicate in aClause:
        newTerms= ()
        terms = predicate[1][2] if predicate[0] == 'NOT' else predicate[2]
        for t in terms:
            newT = t
            while newT in aTheta:
                newT = aTheta[newT]
            newTerms += (newT,)
        newPredicate = ('NOT', ('PREDICATE', predicate[1][1], newTerms)) if predicate[0] == 'NOT' else ('PREDICATE', predicate[1],  newTerms)
        newClause += (newPredicate,)
        aClause = newClause
    return aClause
    
#Resolves 2 clauses
def Resolve(aClause1, aClause2):        
    result = []
    aClause1, aClause2 = StandardizeVar(aClause1, aClause2)
    #Resolve every predicate of c1 with every predicate of c2
    for i in xrange(len(aClause1)):
        leftPredicate = aClause1[i]
        for j in xrange(len(aClause2)):
            rightPredicate = aClause2[j]
            theta = None
            if leftPredicate[0] == 'NOT' and rightPredicate[0] == 'PREDICATE':
                #Unify the 2 predicates
                theta = Unify(leftPredicate[1], rightPredicate)
            elif rightPredicate[0] == 'NOT' and leftPredicate[0] == 'PREDICATE':
                #Unify the 2 predicates
                theta = Unify(leftPredicate, rightPredicate[1])
            if theta is not None:
                newC1 = aClause1[0:i] + aClause1[i+1:]
                newC1 = Substitute(newC1, theta)
                newC2 = aClause2[0:j] + aClause2[j+1:]
                newC2 = Substitute(newC2, theta)
                combinedClause = newC1 + newC2
                result.append(combinedClause)
    return result
    
def FactorMultipleClauses(aClauses):
    result = []
    for c in aClauses:
        result.extend(Factor(c))
    return result
    
#Need standardize variables
def StandardizeVar(aClause1, aClause2):
    #Find all variables that exist in aClause1
    varFound = set()
    for predicate in aClause1:
        terms = predicate[1][2] if predicate[0] == 'NOT' else predicate[2]
        for t in terms:
            if t[0] == 'VARIABLE':
                varFound.add(t)
    #Find all variables that exist in aClause2
    for predicate in aClause2:
        terms = predicate[1][2] if predicate[0] == 'NOT' else predicate[2]
        for t in terms:
            if t[0] == 'VARIABLE':
                varFound.add(t)
    #Build new substitution list
    newSubstitution = {}
    i = 0
    for predicate in aClause2:
        terms = predicate[1][2] if predicate[0] == 'NOT' else predicate[2]
        for t in terms:
            if t[0] == 'VARIABLE' and t not in newSubstitution:
                #Get a unique variable
                while True:
                    newVar = str(i)
                    i += 1    
                    if ('VARIABLE', newVar) not in varFound:
                        break                
                newSubstitution[t] = ('VARIABLE', newVar)
    return aClause1, Substitute(aClause2, newSubstitution)
 
#Check if aClause1 is subsumbed by aKbClause (based on online resource)
#def IsSubsumedBy(aClause1, aKbClause):                        
#    constFound = set()
#    for predicate in aClause1:
#        newTerms= ()
#        terms = predicate[1][2] if predicate[0] == 'NOT' else predicate[2]
#        for t in terms:
#            if t[0] == 'CONSTANT':
#                constFound.add(t)
#                
#    for predicate in aKbClause:
#        newTerms= ()
#        terms = predicate[1][2] if predicate[0] == 'NOT' else predicate[2]
#        for t in terms:
#            if t[0] == 'CONSTANT':
#                constFound.add(t)
#                
#    #Assign unique constants to each unqiue variables in aClause1
#    i = 0
#    W = []
#    varSubstituted = {}
#    for predicate in aClause1:
#        newTerms= ()
#        terms = predicate[1][2] if predicate[0] == 'NOT' else predicate[2]
#        for t in terms:
#            if t[0] == 'VARIABLE':
#                if t not in varSubstituted:
#                    while ('CONSTANT', str(i)) in constFound:
#                        i += 1                    
#                    varSubstituted[t] = ('CONSTANT', str(i))                    
#                    i += 1
#                newTerms += (varSubstituted[t],)
#            else:
#                newTerms += (t,)
#        if predicate[0] == 'NOT':
#            W.append(('PREDICATE', predicate[1][1], newTerms))
#        else:
#            W.append(('NOT', ('PREDICATE', predicate[1], newTerms)))
#        
#    U = [aKbClause]
#    while len(U) > 0:
#        newU = []
#        for clause in U:
#            for predicate in W:
#                resolvents = Resolve(clause, (predicate,))
#                for c in resolvents:
#                    if c == ():
#                        return True
#                    newU.append(c)
#        U = newU
#    return False
   
#Check if aClause1 is subsumbed by aKbClause (my own derivation)
def IsSubsumedBy(aClause1, aKbClause):                
    def RecurrIsSubsumedBy(c1, c2):
        if c1 == c2:
            return True
        if len(c2) == 0:
            return True
        for i in xrange(len(c1)):
            theta = Unify(c1[i], c2[0])
            if theta is not None:
                #Remove the 2 predicates and recursively go down
                if RecurrIsSubsumedBy(Substitute(c1[0:i] + c1[i+1:], theta), Substitute(c2[1:], theta)):
                    return True
        return False
        
    constFound = set()
    for predicate in aClause1:
        newTerms= ()
        terms = predicate[1][2] if predicate[0] == 'NOT' else predicate[2]
        for t in terms:
            if t[0] == 'CONSTANT':
                constFound.add(t)
                
    for predicate in aKbClause:
        newTerms= ()
        terms = predicate[1][2] if predicate[0] == 'NOT' else predicate[2]
        for t in terms:
            if t[0] == 'CONSTANT':
                constFound.add(t)
                
    #Assign unique constants to each unqiue variables in aClause1
    i = 0
    newClause1 = ()
    varSubstituted = {}
    for predicate in aClause1:
        newTerms= ()
        terms = predicate[1][2] if predicate[0] == 'NOT' else predicate[2]
        for t in terms:
            if t[0] == 'VARIABLE':
                if t not in varSubstituted:
                    while ('CONSTANT', str(i)) in constFound:
                        i += 1                    
                    varSubstituted[t] = ('CONSTANT', str(i))                    
                    i += 1
                newTerms += (varSubstituted[t],)
            else:
                newTerms += (t,)                    
        newClause1 += (('NOT' ,('PREDICATE', predicate[1][1], newTerms)),) if predicate[0] == 'NOT' else (('PREDICATE', predicate[1], newTerms),)
    
    return RecurrIsSubsumedBy(newClause1, aKbClause)            
 
#Check if clause is a tautology
def IsTautology(aClause):
    for i in xrange(len(aClause)):
        leftPredicate = aClause[i]
        for j in xrange(i + 1, len(aClause)):
            rightPredicate= aClause[j]
            if leftPredicate[0] == 'NOT' and rightPredicate[0] != 'NOT':
                if leftPredicate[1] == rightPredicate:
                    return True
            elif rightPredicate[0] == 'NOT' and leftPredicate[0] != 'NOT':
                if rightPredicate[1] == leftPredicate:
                    return True
    return False
   
#Factoring (reduces 2 unifiable literals in a clause to 1 if they are unifiable)
#def Factor(aClause):
#    result = []
#    for i in xrange(len(aClause)):
#        for j in xrange(i + 1, len(aClause)):
#            theta = Unify(aClause[i], aClause[j]) 
#            if theta is not None:
#                result.append(Substitute(aClause[0:j] + aClause[j+1:], theta))
#    if len(result) == 0:
#        result.append(aClause)
#    return result
  
#Recursive factoring, will exhaustively reduce all pairs of unifiable literals
def Factor(aClause):
    result = []
    hasVisited = set()
    def RecurrFactor(c):
        hasRemoved = False
        for i in xrange(len(c)):
            for j in xrange(i + 1, len(c)):
                theta = Unify(c[i], c[j]) 
                if theta is not None:
                    hasRemoved = True
                    newC = Substitute(c[0:j] + c[j+1:], theta)
                    if newC not in hasVisited:
                        RecurrFactor(newC)
                        hasVisited.add(newC)
        if not hasRemoved:
            result.append(c)
    RecurrFactor(aClause)
    return result

def GetResolvingClauses(aClause, aPredicateIndex):
    resolvingSet = set()
    #for each predicate in clause
    for predicate in aClause:
        #Get the resolving predicate name
        unifyingPredicateName = GetPredicateName(predicate)
        #Negate the predicate name because we want to cancel out using resolution
        unifyingPredicateName = unifyingPredicateName[1:] if unifyingPredicateName[0] == '~' else '~' + unifyingPredicateName
        #Find resolving clauses
        if unifyingPredicateName in aPredicateIndex:
            resolvingSet = resolvingSet.union(aPredicateIndex[unifyingPredicateName])
    return resolvingSet
    
def GetSimilarClauses(aClause, aPredicateIndex):
    similarClauses = set()
    for p in aClause:
        predName = GetPredicateName(p)
        if predName in aPredicateIndex:
            similarClauses = similarClauses.union(aPredicateIndex[predName])
    return similarClauses

#Returns true of aQuery can be inferred from aKB
def Infer(aKB, aQuery):
#    global numOfResolvedClauses #for testing
#    numOfResolvedClauses = 0 #for tesing
    negatedQuery = ("NOT", aQuery)
    negatedQueryClause = (MoveNegInwards(negatedQuery),)
    openQ = deque()
    #Build predicate index
    predicateIndex = {}
    for clause in aKB:
        UpdatePredicateIndex(clause, predicateIndex)
    UpdatePredicateIndex(negatedQueryClause, predicateIndex)                
    for resolvingClause in GetResolvingClauses(negatedQueryClause, predicateIndex):
        openQ.append((negatedQueryClause, resolvingClause))
        
    while len(openQ) > 0:
        newClauses = set()
        clause1, clause2 = openQ.popleft()
        for c in FactorMultipleClauses(Resolve(clause1, clause2)):
            #numOfResolvedClauses += 1 #for testing
            #if empty clause is in result, return true
            if c == ():
                return True
            if not IsTautology(c):
                newClauses.add(c)               
        for c in newClauses:
            #Try unify with clauses existing in KB                       
            existsInKB = False
            for c2 in GetSimilarClauses(c, predicateIndex):
                if IsSubsumedBy(c, c2):
                    existsInKB = True
                    break
            if not existsInKB:
                #print ClauseDumpS(c)               
                for resolvingClause in GetResolvingClauses(c, predicateIndex):
                    openQ.append((c, resolvingClause))
                UpdatePredicateIndex(c, predicateIndex)
    return False

queries, kb = LoadInput('input.txt')
with open('output.txt', 'w') as f:
    for q in queries:
        f.write('TRUE' if Infer(kb, q) else 'FALSE')
        f.write('\n')
        
#for filename in os.listdir('C:\\Users\\caixi\\Desktop\\DamienTestInput'):
#    queries, kb = LoadInput('C:\\Users\\caixi\\Desktop\\DamienTestInput\\' + filename)
#    with open('C:\\Users\\caixi\\Desktop\\DamienTestInput\\output'+filename[len('input'):-4]+'.txt', 'w') as f:
#        for q in queries:
#            f.write('TRUE' if Infer(kb, q) else 'FALSE')
#            f.write('\n')
            #print "Resolved ", numOfResolvedClauses, " clauses" #for testing
