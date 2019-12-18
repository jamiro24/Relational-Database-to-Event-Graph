const express = require('express');
const router = express.Router();

/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index', {});
});

router.get('/2', function(req, res, next) {
  res.render('index2', {});
});

module.exports = router;
