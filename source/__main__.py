from beartype.claw import beartype_this_package

beartype_this_package()

from source.ui.main import main
from source.logic.track_test import track_test


track_test()
main()
