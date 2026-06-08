_mock.create global_mock
function test_func {
    global_mock.mock.assert_called_once_with "hello"
}
