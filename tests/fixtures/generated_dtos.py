"""
Do not edit! 

This file was automatically generated from: 
/Users/krac/Projects/kodemore/opyapi/tests/fixtures/openapi.yml

Generation time: 
2021-10-15 16:05:02.122194 
"""

import datetime
import typing
import decimal
import ipaddress
import dataclasses


@dataclasses.dataclass()
class NewPet:
    name: str
    base_tag: typing.Optional[str]


@dataclasses.dataclass()
class PetTag:
    name: typing.Optional[str]
    id: typing.Optional[int]


@dataclasses.dataclass()
class Error:
    code: int
    message: str


@dataclasses.dataclass()
class Pet(NewPet):
    id: int
    tags: typing.Optional[typing.List["PetTag"]]
