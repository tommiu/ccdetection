/**
   (Optimized) Match-traversals for function declarations.
*/

/**
   Traverse to function/method declarations enclosing supplied AST
   nodes. This may be the node itself.
*/
Gremlin.defineStep('functions', [Vertex, Pipe], {
  _().ifThenElse{ isFunction(it) }
  { it }
  { it.parents().loop(1){ !isFunction(it.object) } }
});


/**
   Traverse to function/method nodes OR file nodes enclosing supplied
   AST nodes, and back to the corresponding AST_STMT_LIST. This may be
   the node itself. This is particularly useful in PHP since code may
   be declared either in functions *or* top-level.
*/
Gremlin.defineStep('fileOrFunctionStmts', [Vertex, Pipe], {
  _().ifThenElse{ isFunction(it) || it.type == TYPE_FILE }
  { it }
  { it.in().loop(1){ !isFunction(it.object) && it.object.type != TYPE_FILE } }
  .out().filter{ it.type == TYPE_STMT_LIST }
});


// checks whether a given node represents a function/method declaration
Object.metaClass.isFunction = { it ->
  it.type == TYPE_FUNC_DECL ||
  it.type == TYPE_METHOD
  // TODO what about closures?
}

// checks whether a given node is declared within a function/method
// (as opposed to top-level code)
Object.metaClass.isWithinFunction = { it ->
  it.functions().count() > 0
}
