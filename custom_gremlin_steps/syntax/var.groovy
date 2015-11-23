/*
  Traversals for variables.
 */


/**
   Traverse from an AST_VAR node to the name of the variable
 */
Gremlin.defineStep('varToName', [Vertex, Pipe], {
  _().filter{ it.type == TYPE_VAR }.ithChildren(0).code
})


