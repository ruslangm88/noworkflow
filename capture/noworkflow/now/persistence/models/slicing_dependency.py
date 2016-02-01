# Copyright (c) 2016 Universidade Federal Fluminense (UFF)
# Copyright (c) 2016 Polytechnic Institute of New York University.
# This file is part of noWorkflow.
# Please, consult the license terms in the LICENSE file.
"""Slicing Dependency Model"""
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

import textwrap

from future.utils import with_metaclass
from sqlalchemy import Column, Integer
from sqlalchemy import PrimaryKeyConstraint, ForeignKeyConstraint

from .. import relational

from .base import set_proxy, proxy_attr


class SlicingDependency(relational.base):
    """Slicing Dependency Table
    Store slicing dependencies between variables from execution provenance
    """
    __tablename__ = "slicing_dependency"
    __table_args__ = (
        PrimaryKeyConstraint("trial_id", "id"),
        ForeignKeyConstraint(["trial_id"],
                             ["trial.id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["trial_id", "dependent_activation_id"],
                             ["function_activation.trial_id",
                              "function_activation.id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["trial_id", "supplier_activation_id"],
                             ["function_activation.trial_id",
                              "function_activation.id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["trial_id",
                              "dependent_activation_id",
                              "dependent_id"],
                             ["slicing_variable.trial_id",
                              "slicing_variable.activation_id",
                              "slicing_variable.id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["trial_id",
                              "supplier_activation_id",
                              "supplier_id"],
                             ["slicing_variable.trial_id",
                              "slicing_variable.activation_id",
                              "slicing_variable.id"], ondelete="CASCADE"),
    )
    trial_id = Column(Integer, index=True)
    id = Column(Integer, index=True)
    dependent_activation_id = Column(Integer, index=True)
    dependent_id = Column(Integer, index=True)
    supplier_activation_id = Column(Integer, index=True)
    supplier_id = Column(Integer, index=True)

    # _trial: Trial._slicing_dependencies backref
    # _dependent_activation: Activation._slicing_dependents backref
    # _supplier_activation: Activation._slicing_suppliers backref
    # _dependent: SlicingVariable._suppliers_dependencies backref
    # _supplier: SlicingVariable._dependents_dependencies backref


class SlicingDependencyProxy(with_metaclass(set_proxy(SlicingDependency))):
    """SlicingDependency proxy

    Use it to have different objects with the same primary keys
    Use it also for re-attaching objects to SQLAlchemy (e.g. for cache)
    """

    dependent = proxy_attr("_dependent")
    supplier = proxy_attr("_supplier")

    @classmethod
    def to_prolog_fact(cls):
        return textwrap.dedent("""
            %
            % FACT: dependency(trial_id, id, dependent_activation_id, dependent_id, supplier_activation_id, supplier_id).
            %
            """)

    @classmethod
    def to_prolog_dynamic(cls):
        return ":- dynamic(dependency/6)."

    @classmethod
    def to_prolog_retract(cls, trial_id):
        return "retract(usage({}, _, _, _, _, _))".format(trial_id)

    def to_prolog(self):
        return (
            "dependency("
            "{self.trial_id}, {self.id}, "
            "{self.dependent_activation_id}, {self.dependent_id}, "
            "{self.supplier_activation_id}, {self.supplier_id})."
        ).format(**locals())

    def __repr__(self):
        return (
            "SlicingDependency({0.trial_id}, {0.id}, "
            "{0.dependent}, {0.supplier})"
        ).format(self)

    def __str__(self):
        return "{0.dependent} <- {0.supplier}".format(self)
