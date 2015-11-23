/**
   (Optimized) Match-traversals for parameters.
*/

/**
   Given a set of parameters, returns the parameter types.
 */
Gremlin.defineStep('paramsToTypes', [Vertex,Pipe], {
  _().filter{ it.type == TYPE_PARAM }.ithChildren(0)
})


/**
   Given a set of parameters, returns the parameter names.
 */
Gremlin.defineStep('paramsToNames', [Vertex,Pipe], {
  _().filter{ it.type == TYPE_PARAM }.ithChildren(1)
})


/**
   Given a set of parameters, returns the parameter default values.
 */
Gremlin.defineStep('paramsToDefaults', [Vertex,Pipe], {
  _().filter{ it.type == TYPE_PARAM }.ithChildren(2)
})


