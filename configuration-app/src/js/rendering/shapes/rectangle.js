"use strict";

const DEFAULT_COLOR = [0.0, 0.0, 0.0];

import {Node} from "../scene-graph.js";

export default class Rectangle extends Node {
  constructor(x, y, width, height, color) {
    super({
      color: color || DEFAULT_COLOR,
    });

    this._texture = undefined;
    this._x = x;
    this._y = y;
    this._width = width;
    this._height = height;
    this._vertices = this._calculateVertices();
  }

  get x() { return this._x; }

  get y() { return this._y; }

  adjustForDrag(x, y) {
    this.setPosition(x - this._width / 2, y - this._height / 2);
  }

  containsPoint(x, y) {
    return x >= this._x && x <= this._x + this._width &&
           y >= this._y && y <= this._y + this._height;
  }

  setPosition(x, y) {
    super.setPosition(x, y);
    this._x = x;
    this._y = y;
    this._vertices = this._calculateVertices(x, y);
  }

  _calculateVertices(x, y, width, height) {
    x = x || this._x;
    y = y || this._y;
    width = width || this._width;
    height = height || this._height;

    return [
      x, y,
      x, y + height,
      x + width, y + height,
      x + width, y,
    ];
  }

  _renderModel(gl, buffers, model) {
    gl.bindBuffer(gl.ARRAY_BUFFER, buffers.vertexes[0]);
    gl.vertexAttribPointer(model.coordinatesAttrib, 2, gl.FLOAT, false, 0, 0);
    gl.enableVertexAttribArray(model.coordinatesAttrib);

    const vertices = this.vertices;
    gl.uniformMatrix4fv(model.location, false, this.modelMatrix.elements);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertices), gl.STATIC_DRAW);
    gl.drawArrays(gl.TRIANGLE_FAN, 0, vertices.length / 2);
  }

  _renderTexture(gl, textureSpec) {
    if (!this._texture) {
      this._loadTexture(gl);
    }

    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, this._texture);
    gl.uniform1i(textureSpec.samplerLocation, 0);
    gl.bindBuffer(gl.ARRAY_BUFFER, this._textureCoordBuffer);
    gl.vertexAttribPointer(textureSpec.coordAttrib, 2, gl.FLOAT, false, 0, 0);
    gl.enableVertexAttribArray(textureSpec.coordAttrib);
  }

  _loadTexture(gl) {
    this._texture = gl.createTexture();

    const level = 0;
    const internalFormat = gl.RGBA;
    const width = 1;
    const height = 1;
    const border = 0;
    const srcFormat = gl.RGBA;
    const srcType = gl.UNSIGNED_BYTE;
    const pixel = new Uint8Array([0, 0, 0, 0]);  // opaque blue

    gl.activeTexture(gl.TEXTURE1);
    gl.bindTexture(gl.TEXTURE_2D, this._texture);
    gl.texImage2D(gl.TEXTURE_2D, level, internalFormat,
                  width, height, border, srcFormat, srcType,
                  pixel);

    this._textureCoordBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, this._textureCoordBuffer);
    const textureCoordinates = [
      0.0, 0.0,
      0.0, 1.0,
      1.0, 1.0,
      1.0, 0.0,
    ];

    gl.bindBuffer(gl.ARRAY_BUFFER, this._textureCoordBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(textureCoordinates),
                  gl.STATIC_DRAW);
  }
}
