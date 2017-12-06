"use strict";

import Events from "../../events/events.js";
import TextConstants from "../text-constants.js";
import Rectangle from "./rectangle.js";

export default class SingleLineText extends Rectangle {
  constructor(x, y, width, height, color, textProps) {
    super(x, y, width, height, color);

    this._texture = undefined;
    this._textureCoordsBuffer = undefined;
    this._textImage = undefined;

    this._textProps = textProps || { };
    Object.assign(this._textProps, TextConstants.fontProperties);
  }

  get text() { return this._text; }
  set text(value) {
    this._text = value;
    this._textGenerator.setDimensions(this._width, this._height);

    const textResult = this._textGenerator.renderText(this._text, this._textProps);

    this._textImage = new Image();
    this._textImage.width = textResult.width;
    this._textImage.height = textResult.height;
    this._textImage.src = textResult.toDataURL();
    this._textImage.addEventListener("load", () => {
      this._texture = undefined;
      Events.invalidateSceneGraph(this.sceneGraph);
    });
  }

  get width() { return this._width; }
  get height() { return this._height; }

  _renderTexture(gl, textureSpec) {
    if (!this._texture) {
      this._loadTextTexture(gl, textureSpec);
    }

    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, this._texture);
    gl.uniform1i(textureSpec.samplerLocation, 0);

    gl.bindBuffer(gl.ARRAY_BUFFER, this._textureCoordsBuffer);
    gl.vertexAttribPointer(textureSpec.coordAttrib, 2, gl.FLOAT, false, 0, 0);
    gl.enableVertexAttribArray(textureSpec.coordAttrib);
  }

  _loadTextTexture(gl, textureSpec) {
    this._texture = gl.createTexture();
    this._textureCoordsBuffer = gl.createBuffer();

    gl.bindTexture(gl.TEXTURE_2D, this._texture);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, this._textImage);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.bindTexture(gl.TEXTURE_2D, null);

    const textureCoordinates = [
      0.0, 0.0,
      0.0, 1.0,
      1.0, 1.0,
      1.0, 0.0,
    ];

    gl.bindBuffer(gl.ARRAY_BUFFER, this._textureCoordsBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(textureCoordinates),
                  gl.STATIC_DRAW);
  }
}
