"use strict";

export default class Renderer {
  constructor(canvas, sceneGraph) {
    this._canvas = canvas;
    this._canvas.style.width = `${this._canvas.width}px`;
    this._canvas.style.height = `${this._canvas.height}px`;
    this._canvas.width *= window.devicePixelRatio;
    this._canvas.height *= window.devicePixelRatio;
    this._sceneGraph = sceneGraph;
    this._sceneWidth = this._canvas.width;
    this._sceneHeight = this._canvas.height;
    this._gl = canvas.getContext("webgl", {
      antialias: true,
      alpha: true,
      depth: true,
    });
    this._projectionMatrix = glm.ortho(0.0, this._sceneWidth, this._sceneHeight, 0.0);
    this._shaderProgram = undefined;
    this._projectionLocation = undefined;
    this._buffers = {};
    this._model = {};
    this._texture = {};

    this._initRenderingContext();
    this._initBuffers();
  }

  render() {
    if (this._sceneGraph.dirty) {
      this._draw();
    }

    this._sceneGraph.dirty = false;
    window.requestAnimationFrame(() => this.render());
  }

  _draw() {
    this._gl.clearColor(1.0, 1.0, 1.0, 1.0);
    this._gl.enable(this._gl.DEPTH_TEST);
    this._gl.clear(this._gl.COLOR_BUFFER_BIT);
    this._gl.viewport(0, 0, this._sceneWidth, this._sceneHeight);

    this._gl.bindBuffer(this._gl.ARRAY_BUFFER, this._vertexBuffer);
    this._gl.uniformMatrix4fv(this._projectionLocation, false, this._projectionMatrix.elements);

    this._sceneGraph.nodes.forEach((node) => {
      node.children.forEach((child) => {
        this._gl.bindBuffer(this._gl.ARRAY_BUFFER, this._buffers.colors[0]);
        this._gl.bufferData(this._gl.ARRAY_BUFFER, new Float32Array(child.color), this._gl.STATIC_DRAW);
        this._gl.vertexAttribPointer(this._colorAttrib, 4, this._gl.FLOAT, false, 0, 0);
        this._gl.enableVertexAttribArray(this._colorAttrib);
        this._gl.bindBuffer(this._gl.ARRAY_BUFFER, null);

        child.render(this._gl, this._buffers, this._model, this._texture);
      });

      this._gl.bindBuffer(this._gl.ARRAY_BUFFER, this._buffers.colors[0]);
      this._gl.bufferData(this._gl.ARRAY_BUFFER, new Float32Array(node.color), this._gl.STATIC_DRAW);
      this._gl.vertexAttribPointer(this._colorAttrib, 4, this._gl.FLOAT, false, 0, 0);
      this._gl.enableVertexAttribArray(this._colorAttrib);
      this._gl.bindBuffer(this._gl.ARRAY_BUFFER, null);

      node.render(this._gl, this._buffers, this._model, this._texture);
    });

    this._gl.bindBuffer(this._gl.ARRAY_BUFFER, null);
  }

  _initBuffers() {
    this._buffers.vertexes = [this._gl.createBuffer()];
    this._buffers.colors = [this._gl.createBuffer()];
  }

  _initRenderingContext() {
    const vertCode = `
      attribute vec2 coordinates;
      attribute vec4 vertexColor;
      attribute vec2 textureCoords;

      uniform mat4 modelMatrix;
      uniform mat4 projectionMatrix;

      varying lowp vec4 vColor;
      varying highp vec2 tCoords;

      void main() {
        gl_Position = projectionMatrix * modelMatrix * vec4(coordinates, 0.0, 1.0);
        vColor = vertexColor;
        tCoords = textureCoords;
      }
    `;

    const vertShader = this._gl.createShader(this._gl.VERTEX_SHADER);
    this._gl.shaderSource(vertShader, vertCode);
    this._gl.compileShader(vertShader);

    const fragCode = `
      varying lowp vec4 vColor;
      varying highp vec2 tCoords;

      uniform sampler2D texSampler;

      void main(void) {
        highp vec4 tex = texture2D(texSampler, vec2(tCoords.s, tCoords.t));
        highp float alpha = max(tex.a, vColor.a);
        gl_FragColor = vec4(mix(min(tex.r, vColor.r), max(tex.r, vColor.r), alpha),
                            mix(min(tex.g, vColor.g), max(tex.g, vColor.g), alpha),
                            mix(min(tex.b, vColor.b), max(tex.b, vColor.b), alpha),
                            alpha);
      }
    `;

    const fragShader = this._gl.createShader(this._gl.FRAGMENT_SHADER);
    this._gl.shaderSource(fragShader, fragCode);
    this._gl.compileShader(fragShader);

    this._shaderProgram = this._gl.createProgram();
    this._gl.attachShader(this._shaderProgram, vertShader);
    this._gl.attachShader(this._shaderProgram, fragShader);

    this._gl.linkProgram(this._shaderProgram);
    this._gl.useProgram(this._shaderProgram);

    this._projectionLocation = this._gl.getUniformLocation(this._shaderProgram, "projectionMatrix");
    this._model = {
      location: this._gl.getUniformLocation(this._shaderProgram, "modelMatrix"),
      coordinatesAttrib: this._gl.getAttribLocation(this._shaderProgram, "coordinates"),
    };

    this._colorAttrib = this._gl.getAttribLocation(this._shaderProgram, "vertexColor");
    this._texture = {
      coordAttrib: this._gl.getAttribLocation(this._shaderProgram, "textureCoords"),
      samplerLocation: this._gl.getUniformLocation(this._shaderProgram, "texSampler"),
    };
  }
}
