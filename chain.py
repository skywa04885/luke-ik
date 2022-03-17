from helpers import generalize_unit, rad
from bone_vector import bone_vector

chain_top = bone_vector.rotational(
    vector_length=generalize_unit(34.0, 'mm'),
    theta=rad(0),
    theta_min=rad(-120),
    theta_max=rad(120)
)

chain_middle = bone_vector.rotational(
    vector_length=generalize_unit(30.5, 'mm'),
    next=chain_top,
    theta=rad(0),
    theta_min=rad(-90),
    theta_max=rad(90)
)

chain_bottom = bone_vector.twisting(
    theta=rad(0.0),
    vector_length=generalize_unit(0, 'mm'),
    next=chain_middle,
    theta_min=rad(-180.0),
    theta_max=rad(180.0)
)

def chain_init() -> None:
    chain_bottom.link()
