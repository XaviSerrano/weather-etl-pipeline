
import logging
from unittest.mock import Mock

import pytest
import main


# 1. Comprobamos que las tres fases se ejecutan en el orden correcto.
def test_main_executes_pipeline_in_correct_order(monkeypatch):
    execution_order = []

    monkeypatch.setattr(
        main,
        "run_extract",
        lambda: execution_order.append("extract")
    )
    monkeypatch.setattr(
        main,
        "run_transform",
        lambda: execution_order.append("transform")
    )
    monkeypatch.setattr(
        main,
        "run_load",
        lambda: execution_order.append("load")
    )

    main.main()

    assert execution_order == ["extract", "transform", "load"]


# 2. Comprobamos que un error en la extracción detiene la pipeline.
def test_main_stops_when_extraction_fails(monkeypatch):
    mock_extract = Mock(side_effect=Exception("Error de extracción"))
    mock_transform = Mock()
    mock_load = Mock()

    monkeypatch.setattr(main, "run_extract", mock_extract)
    monkeypatch.setattr(main, "run_transform", mock_transform)
    monkeypatch.setattr(main, "run_load", mock_load)

    with pytest.raises(SystemExit) as error:
        main.main()

    assert error.value.code == 1
    mock_extract.assert_called_once()
    mock_transform.assert_not_called()
    mock_load.assert_not_called()


# 3. Comprobamos que un error en la transformación impide la carga.
def test_main_stops_when_transformation_fails(monkeypatch):
    mock_extract = Mock()
    mock_transform = Mock(
        side_effect=Exception("Error de transformación")
    )
    mock_load = Mock()

    monkeypatch.setattr(main, "run_extract", mock_extract)
    monkeypatch.setattr(main, "run_transform", mock_transform)
    monkeypatch.setattr(main, "run_load", mock_load)

    with pytest.raises(SystemExit) as error:
        main.main()

    assert error.value.code == 1
    mock_extract.assert_called_once()
    mock_transform.assert_called_once()
    mock_load.assert_not_called()


# 4. Comprobamos que la pipeline finaliza correctamente.
def test_main_logs_success_message(monkeypatch, caplog):
    monkeypatch.setattr(main, "run_extract", Mock())
    monkeypatch.setattr(main, "run_transform", Mock())
    monkeypatch.setattr(main, "run_load", Mock())

    with caplog.at_level(logging.INFO):
        main.main()

    assert "PIPELINE FINALIZADA CORRECTAMENTE" in caplog.text
