from beartype.claw import beartype_this_package

beartype_this_package()

from source.ui.main import main
from source.logic.physics_test import test_all

test_all()
# main()
