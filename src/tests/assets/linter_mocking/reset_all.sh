_mock.create my_mock
_mock.reset_all
my_mock.mock.assert_called_once_with "hello"
