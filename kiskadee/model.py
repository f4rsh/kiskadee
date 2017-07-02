"""This module provides kiskadee database model."""

import kiskadee.database
import kiskadee.model
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, UnicodeText, UniqueConstraint,\
                       Sequence, Unicode, ForeignKey, Boolean, orm

Base = declarative_base()


class Package(Base):
    """Software packages abstraction.

    A software package is the source code for a software project. It may be
    upstream's distribution or the sources provided by some other source, like
    a linux distribution.
    """

    __tablename__ = 'packages'
    id = Column(Integer,
                Sequence('packages_id_seq', optional=True), primary_key=True)
    name = Column(Unicode(255), nullable=False)
    plugin_id = Column(Integer, ForeignKey('plugins.id'), nullable=False)
    versions = orm.relationship('Version', backref='packages')
    __table_args__ = (
            UniqueConstraint('name', 'plugin_id'),
            )


class Plugin(Base):
    """kiskadee plugin abstraction."""

    __tablename__ = 'plugins'
    id = Column(Integer,
                Sequence('plugins_id_seq', optional=True), primary_key=True)
    name = Column(Unicode(255), nullable=False, unique=True)
    target = Column(Unicode(255), nullable=True)
    description = Column(UnicodeText)
    packages = orm.relationship('Package', backref='plugins')


class Version(Base):
    """Abstraction of a package version."""

    __tablename__ = 'versions'
    id = Column(Integer,
                Sequence('versions_id_seq', optional=True), primary_key=True)
    number = Column(Unicode(100), nullable=False)
    package_id = Column(Integer, ForeignKey('packages.id'), nullable=False)
    analysis = orm.relationship('Analysis', backref='versions')
    __table_args__ = (
            UniqueConstraint('number', 'package_id'),
            )

class Analyzer(Base):
    """Abstraction of a static analyzer."""

    __tablename__ = 'analyzers'
    id = Column(Integer,
                Sequence('analyzers_id_seq', optional=True), primary_key=True)
    name = Column(Unicode(255), nullable=False, unique=True)
    version = Column(Unicode(255), nullable=True)
    analysis = orm.relationship('Analysis', backref='analyzers')


class Analysis(Base):
    """Abstraction of a package analysis."""

    __tablename__ = 'analysis'
    id = Column(Integer,
                Sequence('analysis_id_seq', optional=True), primary_key=True)
    version_id = Column(Integer, ForeignKey('versions.id'), nullable=False)
    analyzer_id = Column(Integer, ForeignKey('analyzers.id'), nullable=False)
    raw = Column(UnicodeText)
