"use strict";

/**
 * Provides an implementation of text to texture generation which relies on canvas 2d.
 * This is not ideal, but it should offer decent performance for bravehub.
 */
class TextGenerator {
  constructor() {
    this._canvas = document.createElement("canvas");
    this._canvas.style.visibility = "hidden";
    this._canvasCtx = this._canvas.getContext("2d");

    document.body.appendChild(this._canvas);
  }

  /**
   * Text generator is leased to a specific consumer which aims to edit text.
   * It is the consumer responsibility to set the boundaries for the text generator
   * based on its desired dimensions.
   *
   * @param {Number} width the maximum width of the viewable area.
   * @param {Number} height the maximum height of the viewable area.
   */
  setDimensions(width, height) {
    this._downscaleFactor = 2;
    this._origWidth = width;
    this._origHeight = height;
    this._canvas.width = width * this._downscaleFactor;
    this._canvas.height = height * this._downscaleFactor;
  }

  /**
   * Renders the given text on the current canvas. The whole canvas is returned to the caller
   * so that it can be used for texture generation.
   *
   * @param {String} text the text we want to render.
   * @param {Object} textProps the properties for rendering the text.
   * @param {Number} textProps.size the dimension of the font used for rendering.
   * @param {String} textProps.unit the unit we currently used for font rendering (e.g em / px).
   * @param {String} textProps.family the font family we want to use.
   * @param {String} textProps.fill the fill color we want to apply for the text.
   * @param {String} textProps.align the horizontal text alignment.
   * @param {String} textProps.baseline the reference baseline.
   * @return {Canvas} the actual html canvas from where webgl texture can be generated.
   */
  renderText(text, textProps) {
    this._canvasCtx.clearRect(0, 0, this._canvas.width, this._canvas.height);

    const textSize = textProps.size * this._downscaleFactor;
    textProps.size = textSize;
    this._setFontProperties(textProps);

    this._canvasCtx.width = this._canvasCtx.measureText(text).width * this._downscaleFactor;
    this._canvasCtx.height = textSize;
    this._canvasCtx.scale(window.devicePixelRatio, window.devicePixelRatio);

    this._setFontProperties(textSize);
    this._canvasCtx.fillText(text, 10, 20);

    this._canvasCtx.scale(1 / window.devicePixelRatio, 1 / window.devicePixelRatio);
    this._canvasCtx.scale(1 / this._downscaleFactor, 1 / this._downscaleFactor);

    textProps.size = textSize / this._downscaleFactor;

    return this._canvas;
  }

  _setFontProperties(textProps) {
    this._canvasCtx.font = `${textProps.size}${textProps.unit} ${textProps.family}`;
    this._canvasCtx.fillStyle = textProps.fill;
    this._canvasCtx.textAlign = textProps.align;
    this._canvasCtx.textBaseline = textProps.baseline;
  }
}

const textGenerator = new TextGenerator();
export default textGenerator;
