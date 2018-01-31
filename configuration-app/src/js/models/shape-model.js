"use strict";

import Events from "../events/events.js";
import MessageBus from "../events/message-bus.js";

/**
 * Model provides the interface for adapting custom data source providers to the current shapes. Every model
 * is an event emitter so that it can easily provides observable pattern.
 */
export class Model {
  constructor(data) {
    Object.assign(this, data);
    this._notifier = new MessageBus();
  }

  on(evtName, fn) {
    this._notifier.on(evtName, fn);
  }

  off(evtName, fn) {
    this._notifier.off(evtName, fn);
  }

  /**
   * Fetch the specified model data based on the specified unique identifier.
   *
   * @param {Object} opts contains the unique identifier(s) for the current model.
   * @return {Promise} a promise which resolves to the updated model or rejects with a specific error.
   */
  fetch(opts) { return undefined; }
}

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
