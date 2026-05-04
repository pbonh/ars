test-hermes:
  ./roles/dotfiles/tests/hermes/run-tests.sh

test-hermes-integration:
  HERMES_TEST=1 ./roles/dotfiles/tests/hermes/run-tests.sh

regenerate-hermes-fixtures:
  ./roles/dotfiles/tests/hermes/make-fixtures.sh
