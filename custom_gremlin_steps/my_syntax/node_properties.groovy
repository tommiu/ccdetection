/**
   Return all nodes in the subtrees rooted in the current vertices and
   filter them according to a predicate p.

   @param p The predicate
*/
/*Gremlin.defineStep('hasFlag', [Vertex, Pipe], { p ->
  _().filter{ it.flags[0] == p }
})
*/

Gremlin.defineStep('hasFlag', [Vertex, Pipe], { p ->
  _().filter{ 
                def x = false;
                for (element in it.flags) {
                    if (element == p) x = true
                }
                return x 
            }
})

Object.metaClass.isIfNode = { it -> 
    it.type == TYPE_IF
}
