/**
   Match descriptions as presented in the paper 'Modeling and
   Discovering Vulnerabilities with Code Property Graphs', S&P 2014
   (F. Yamaguchi, N. Golde, D. Arp, K. Rieck). Please note, that
   tradeoffs in efficiency are made for increased robustness and ease
   of formulation.
*/

/**
   Return all nodes in the subtrees rooted in the current vertices and
   filter them according to a predicate p.

   @param p The predicate
*/
Gremlin.defineStep('match', [Vertex, Pipe], { p ->
  _().astNodes().filter( p)
})


/**
   Walk the tree into the direction of the root stopping at the
   enclosing statement and output all parents that match the supplied
   predicate. Note that this may include the enclosing statement node.
*/
Gremlin.defineStep('matchParents', [Vertex,Pipe], { p ->
  _().parents().loop(1){ !isStatement(it.object) }{ p(it.object) }
})


/**
   Searches in all subtrees of the current vertices for call
   expressions and therein for i'th arguments that start with a given
   string f.

   @param start String to match the beginning of an argument
   @param i     The number of the argument
*/
Gremlin.defineStep('arg', [Vertex, Pipe], { start, i ->
  _().match{ isCallExpression(it) && getFuncName(it).startsWith( start) }
  .children().filter{ it.type == TYPE_ARG_LIST }.ithChildren( i)
})


// gets the function name of a call expression
Object.metaClass.getFuncName = { it ->
  if( it.type == TYPE_CALL) {
    // have to call .next() because the calls to ithChildren()
    // implictly convert the vertex 'it' into a Gremlin pipeline, but
    // we know that only one vertex is spit out at the end and we want
    // its 'code' property
    it.ithChildren(0).ithChildren(0).next().code
  }
  else if( it.type == TYPE_STATIC_CALL ||
	   it.type == TYPE_METHOD_CALL ) {
    it.ithChildren(1).next().code
  }
  else {
    null
  }
}


/**
   Searches for all parameter nodes including and below the current
   nodes, and matches them against the regex 'regex'.

   @param regex The regex to match.
*/
Gremlin.defineStep('param', [Vertex, Pipe], { regex ->
  _().match{ it.type == TYPE_PARAM && it.ithChildren(1).next().code.matches( regex) }
})

