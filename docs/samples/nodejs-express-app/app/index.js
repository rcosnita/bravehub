"use strict";
const config = require("./configs/app-meta.json");

const express = require("express");
const app = express();

app.get("/", function (req, res) {
  res.send(JSON.stringify(config))
});

app.listen(80, function () {
  console.log('Example app listening on port 80!')
});
