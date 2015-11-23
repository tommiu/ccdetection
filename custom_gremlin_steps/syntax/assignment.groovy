/**
   (Optimized) Match-traversals for assignments.
*/

// checks whether a given node represents an assignment
Object.metaClass.isAssignment = { it ->
  it.type == TYPE_ASSIGN ||
  it.type == TYPE_ASSIGN_REF ||
  it.type == TYPE_ASSIGN_OP
}

/**
   Traverse to left side of an assignment.
*/
Gremlin.defineStep('lval', [Vertex,Pipe], {
  _().filter{ isAssignment(it) }.ithChildren(0)
});


/**
   Traverse to right side of an assignment.
*/
Gremlin.defineStep('rval', [Vertex,Pipe], {
  _().filter{ isAssignment(it) }.ithChildren(1)
});
