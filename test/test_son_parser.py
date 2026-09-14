import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

import xml2obj
from Main import Accert
from son_parser import son_to_xml


def test_fallback_son_parser_matches_accert_object_shape():
    xml = son_to_xml(PROJECT_ROOT / "tutorial" / "accert" / "LargeTokamak.son")
    document = xml2obj.xml2obj(xml)

    assert str(document.accert.ref_model.value) == '"fusion"'
    assert str(document.accert.l0COA.id) == "2"
    assert str(document.accert.l0COA.l1COA.l2COA.alg.id) == '"acc211"'
    assert str(document.accert.l0COA.l1COA.l2COA.alg.var[0].id) == '"csi"'
    assert str(document.accert.l0COA.l1COA.l2COA.alg.var[0].value.value) == "16"


def test_accert_load_obj_uses_python_fallback_when_sonvalidxml_is_missing(monkeypatch):
    monkeypatch.setenv("ACCERT_SONVALIDXML", str(PROJECT_ROOT / "bin" / "missing-sonvalidxml"))

    accert = Accert(
        PROJECT_ROOT / "tutorial" / "accert" / "LargeTokamak.son",
        PROJECT_ROOT,
    )

    assert str(accert.input.accert.ref_model.value) == '"fusion"'
