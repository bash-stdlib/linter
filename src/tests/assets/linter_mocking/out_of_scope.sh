function test_func {
    _mock.create my_mock
}
my_mock.mock.assert_called_once_with "hello"
