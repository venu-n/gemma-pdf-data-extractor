from app.ollama_provider import _parse_response

def test_parse_json_response():
    result = _parse_response('{"check_number":"0007","issue_date":"Aug. 11, 2019","beneficiary_name":"Mary Johnson","amount":"$715.39","memo":"Monthly rent"}')
    assert result.check_number == '0007'
    assert result.beneficiary_name == 'Mary Johnson'
    assert result.amount == '$715.39'
    assert result.memo == 'Monthly rent'

def test_parse_embedded_json():
    result = _parse_response('Here: {"check_number":"0007","beneficiary_name":"www.psdgraphics.com","amount":"$1.00","memo":"test"}')
    assert result.beneficiary_name == 'www.psdgraphics.com'
