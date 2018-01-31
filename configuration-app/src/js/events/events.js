"use strict";

/**
 * Provides a simple model for handling ui events from the components.
 */
export class UiEvent {
  constructor(eventName, opts) {
    this._eventName = eventName;
    this._node = opts.node;
    this._sceneGraph = opts.sceneGraph;
  }

  get eventName() { return this._eventName; }

  get node() { return this._node; }

  get sceneGraph() { return this._sceneGraph; }
}

/**
 * Provides a simple model for handling model events.
 */
export class ModelEvent {
  constructor(eventName, opts) {
    opts = opts || { };
    this._eventName = eventName;
    this._model = opts.model;
  }

  get eventName() { return this._eventName; }

  get model() { return this._model; }
}

const GESTURES_EVENTS = {
  DELETE_NODE: "gestures:keyboard:node:delete",

  CLOSE_EDITOR: "gestures:synthetic:editor:close",
};

const SCENE_GRAPH_EVENTS = {
  INVALIDATE_SCENE: "scenegraph:global:invalidate",

  NEW_SCENE: "scenegraph:global:new",
};

const MODEL_EVENTS = {
  GET_CURRENT_PROJECT: "models:project:get-current",
  GET_CURRENT_PROJECT_LOADED: "models:project:get-current:loaded",

  SET_CURRENT_PROJECT: "models:project:set-current",
};

/**
 * Provides various event constants used to communicate between components of the canvas.
 */
class Events {
  static get gestures() {
    return GESTURES_EVENTS;
  }

  static get sceneGraph() {
    return SCENE_GRAPH_EVENTS;
  }

  static get models() {
    return MODEL_EVENTS;
  }

  static invalidateSceneGraph(sceneGraph) {
    const evtName = Events.sceneGraph.INVALIDATE_SCENE;
    sceneGraph.messageBus.emit(evtName, new UiEvent(evtName, {
      "sceneGraph": sceneGraph,
    }));
  }

  static newSceneGraph(sceneGraph) {
    const evtName = Events.sceneGraph.NEW_SCENE;
    sceneGraph.messageBus.emit(evtName, new UiEvent(evtName, {
      "sceneGraph": sceneGraph,
    }));
  }
}

export {Events};
export default Events;
