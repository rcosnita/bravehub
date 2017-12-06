"use strict";

import Events from "../events/events.js";

/**
 * Provides an observable model factory for shapes belonging to a scenegraph.
 * Every model mutation will trigger a scene graph invalidation so that rendering works as expected.
 */
export default {
  getModel: function(originalModel, sceneGraphFn, getter, setter) {
    return new Proxy(originalModel, {
      get: (target, name) => {
        return getter(target, name);
      },
      set: (target, name, value) => {
        const sceneGraph = sceneGraphFn();
        const result = setter(target, name, value);

        if (sceneGraph) {
          // there are use cases when the node does not have a scene graph set but we still mutate the model.
          // in this case we do not need to invalidate the scene graph.
          Events.invalidateSceneGraph(sceneGraph);
        }

        return result;
      },
    });
  },
};
