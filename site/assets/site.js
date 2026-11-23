(function () {
  var b = document.querySelector('.burger'), n = document.querySelector('header nav');
  if (b) b.addEventListener('click', function () {
    var o = n.classList.toggle('open');
    b.setAttribute('aria-expanded', o);
  });
  var q = document.getElementById('q');
  if (q) {
    var items = [].slice.call(document.querySelectorAll('.art')),
        c = document.getElementById('count'), none = document.getElementById('none');
    q.addEventListener('input', function () {
      var v = q.value.trim().toLowerCase(), k = 0;
      items.forEach(function (a) {
        var m = !v || a.dataset.q.indexOf(v) > -1;
        a.hidden = !m;
        if (m) k++;
      });
      c.textContent = k + (k === 1 ? ' article' : ' articles');
      none.hidden = k > 0;
    });
  }
})();
