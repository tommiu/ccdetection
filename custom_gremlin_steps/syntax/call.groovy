/**
   (Optimized) Match-traversals for calls.
*/


// checks whether a given node represents a call expression
Object.metaClass.isCallExpression = { it ->
  it.type == TYPE_CALL ||
  it.type == TYPE_STATIC_CALL ||
  it.type == TYPE_METHOD_CALL
}


/**
   Given a set of call expression nodes, returns the corresponding set
   of argument nodes.
 */
Gremlin.defineStep('callToArguments', [Vertex, Pipe], {
  _().children().filter{ it.type == TYPE_ARG_LIST }.children()
})


/**
   Given a set of call expression nodes, returns the corresponding set
   of i'th argument nodes.
 */
Gremlin.defineStep('ithArguments', [Vertex,Pipe], { i -> 
  _().callToArguments().filter{ it.childnum == i }
})


/**
   Given a set of argument nodes, returns the corresponding set of
   call expression nodes.

   Note: It does *not* hold that for any given call expression node v,
   v.callToArguments().argToCall() == v, since v may have 0 arguments
   and hence v.callToArguments() is empty, and therefore
   v.callToArguments().argToCall() is also empty. Additionally, if v
   has more than one argument, then traversing to the arguments and
   back will yield v more than once (use dedup() in such
   cases). However, the equality should hold for all call expressions
   that have exactly one argument.
 */
Gremlin.defineStep('argToCall', [Vertex, Pipe], {
  _().parents().filter{ it.type == TYPE_ARG_LIST }.parents()
})


/**
   For a set of call expressions enclosed in an assign statement,
   traverse to the assign statements that these call expressions are
   enclosed in.
 */
Gremlin.defineStep('callToAssigns', [Vertex, Pipe], {i->
  _().filter{ isCallExpression(it) }.matchParents{ it.type == TYPE_ASSIGN }
})


/**
   Traverse to enclosing call expression.
 */
Gremlin.defineStep('callexpressions', [Vertex, Pipe], {i->
  _().matchParents{ isCallExpression(it) }
})


/**
   Traverse to enclosing call expression.
 */
Gremlin.defineStep('nameToCall', [Vertex, Pipe], {i->
  _().parents().parents()
})


