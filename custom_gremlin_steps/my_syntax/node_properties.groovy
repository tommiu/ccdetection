Gremlin.defineStep('hasFlag', [Vertex, Pipe], { p ->
  _().filter{ 
                def x = false;
                for (element in it.flags) {
                    if (element == p) x = true
                }
                return x 
            }
})

// Generalized node type query.
Object.metaClass.isType = { it, type ->
    it.filter{ it.getProperty("type") == type }.count() == 1
}

AST_EDGE = 'PARENT_OF'
