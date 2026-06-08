function outer {
    function inner {
        _mock.create my_mock
        my_mock.mock.assert_called_once_with "inner"
    }
    my_mock.mock.assert_called_once_with "outer"
}
