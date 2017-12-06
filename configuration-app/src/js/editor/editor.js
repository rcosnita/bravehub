"use strict";

/**
 * Every editor we add to the framework must extend this class. An editor can have a single
 * activeNode at a time. In addition, the editor must provide a dom element which must be presented
 * to the user.
 *
 * At any moment of time every editor must be capable to provide the current value.
 */
export default class Editor {
  constructor() {
    this._activeNode = undefined;
  }

  get activeNode() { return this._activeNode; }

  set activeNode(value) { this._activeNode = value; }

  get domElement() { throw new Error("Each specific editor must override this method ..."); }

  get value() { return this.domElement.value; }

  set value(val) { this.domElement.value = val; }

  /**
   * Each editor should implement this method in order to restore the correct state for
   * the selected node.
   *
   * @param {Object} opts the options we want to use for restoring the editor.
   * @params {Object} opts.model the model belonging to the scene graph node.
   */
  restore(opts) { }

  /**
   * Provides a high level api for positioning the editor at an absolute position.
   *
   * @param {Number} x the horizontal position.
   * @param {Number} y the vertical position.
   */
  setPosition(x, y) {
    this.domElement.style.left = `${x}px`;
    this.domElement.style.top = `${y}px`;
  }
}
