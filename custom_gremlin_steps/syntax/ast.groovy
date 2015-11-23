/**
   Elementrary traversals starting at AST nodes.
*/

/**
   Traverse from root of AST to all nodes it contains
   (including the node itself)
*/
Gremlin.defineStep('astNodes', [Vertex, Pipe], {
  _().transform{
    def x = [] as Set;
    it.children().loop(1){true}{true}
    .store(x).optional(2).transform{x+it}.scatter()
  }.scatter()
})


/**
   Traverse to parent-node of AST nodes.
*/
Gremlin.defineStep('parents', [Vertex, Pipe], {
  _().in(AST_EDGE)
})


/**
   Traverse to child-nodes of AST nodes.
*/
Gremlin.defineStep('children', [Vertex, Pipe], {
  _().out(AST_EDGE)
})


/**
   Traverse to i'th children.
   
   @param i The child index
*/
Gremlin.defineStep('ithChildren', [Vertex, Pipe], { i ->
  _().children().filter{ it.childnum == i }
})


/**
   Traverse to statements enclosing supplied AST nodes. This may be
   the node itself.
*/
Gremlin.defineStep('statements', [Vertex, Pipe], {
  _().ifThenElse{ isStatement(it) }
  { it }
  { it.parents().loop(1){ !isStatement(it.object) } }
});

// A node is a statement node iff its parent is of type TYPE_STMT_LIST
// Note that each node except for the root node has exactly one
// parent, so count() is either 0 or 1
// TODO: we want something more here. In particular, we would also
// like to return 'true' for if/while/for/foreach/... guards (called
// "predicates" in the CFG), and we have to think about what we want
// for statements that enclose other full-fledged statements, e.g., an
// if-statement node which has a body consisting of many other
// statements.
Object.metaClass.isStatement = { it ->
  it.parents().filter{it.type == TYPE_STMT_LIST}.count() == 1
}


/**
   Get number of children of an AST node.
*/
Gremlin.defineStep('numChildren', [Vertex, Pipe], {
  _().transform{ it.children().count() }
})
