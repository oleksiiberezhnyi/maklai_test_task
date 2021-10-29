from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine("sqlite:///parsing_site.db")
DBSession = sessionmaker(bind=engine, )
Base = declarative_base()

session = DBSession()

class Post(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True)
    date = Column(String)
    title = Column(String)
    text = Column(String)
    author = Column(String)
    release_links = relationship("ReleaseLink")

    def __str__(self):
        return self.title


class ReleaseLink(Base):
    __tablename__ = "release_link"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    h1 = Column(String)
    date = Column(String)
    text = Column(String)
    post_id = Column(Integer, ForeignKey("post.id"))
    pep_links = relationship("PepLink")
    files = relationship("Files")

    def __str__(self):
        return self.link


class PepLink(Base):
    __tablename__ = "pep_link"
    id = Column(Integer, primary_key=True)
    link = Column(String)
    release_link_id = Column(Integer, ForeignKey("release_link.id"))

    def __str__(self):
        return self.link


class Files(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    version_link = Column(String)
    operation_system = Column(String)
    description = Column(String)
    md5_sum = Column(String)
    file_size = Column(Integer)
    gpg_link = Column(String)
    release_link_id = Column(Integer, ForeignKey("release_link.id"))

    def __str__(self):
        return self.version_link


Base.metadata.create_all(engine)
