/**
   Given a set of vertices, traverse to the enclosing file nodes.
 */
Gremlin.defineStep('toFile', [Vertex, Pipe], {
  _().in().loop(1){it.object.getProperty("type") != TYPE_FILE}
})

/**
   Given a set of file nodes, return their paths.
 */
Gremlin.defineStep('fileToPath', [Vertex, Pipe], {
  _().filter{ it.getProperty("type") == TYPE_FILE }.sideEffect{ path = it.getProperty("name") }
  .ifThenElse{ it.in(DIRECTORY_EDGE).count() > 0 }
    { it.in(DIRECTORY_EDGE).sideEffect{ path = it.getProperty("name") + "/" + path }.loop(2){it.object.getProperty("id") != 0} }
    { it }
  .transform{ path }
})

