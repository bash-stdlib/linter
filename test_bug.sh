setup() {
  _mock.create hello
}

test_one() {
  hello.mock.get.call 1
}

test_three() {
  hello.mock.get.call 1  # broken, the mock is recreated in setup, it's in the "special global area"
}
