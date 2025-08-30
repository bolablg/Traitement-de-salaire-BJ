import pytest
import json
from unittest.mock import Mock, patch
from main import (
    calculate_tax_details, 
    calculate_gross_from_net, 
    format_french_number, 
    get_max_net_salary,
    get_salary_limits,
    main,
    MAX_GROSS_SALARY
)

class TestSalaryCalculations:
    
    def test_format_french_number(self):
        """Test French number formatting"""
        assert format_french_number(1000) == "1.000"
        assert format_french_number(1000000) == "1.000.000"
        assert format_french_number(500) == "500"

    def test_calculate_tax_details_basic(self):
        """Test basic gross to net calculation"""
        result = calculate_tax_details(100000)
        
        # Should have basic structure
        assert "salaire_brut" in result
        assert "salaire_net" in result
        assert "total_cotisations" in result
        assert "total_impot" in result
        assert "details_cotisations" in result
        assert "details_impot" in result
        
        # Check calculation
        assert result["salaire_brut"] == 100000
        assert result["salaire_net"] > 0
        assert result["salaire_net"] < 100000

    def test_calculate_tax_details_high_salary(self):
        """Test calculation for high salary (multiple tax brackets)"""
        result = calculate_tax_details(600000)
        
        # Should hit multiple tax brackets
        assert len(result["details_impot"]) > 1
        assert result["salaire_brut"] == 600000
        assert result["total_prelevements"] > 0

    def test_calculate_gross_from_net_basic(self):
        """Test basic net to gross calculation"""
        result = calculate_gross_from_net(400000)
        
        # Should have required fields
        assert "salaire_net_desire" in result
        assert "salaire_brut_requis" in result
        assert "details_cotisations" in result
        assert "details_impot" in result
        
        # Check calculation
        assert result["salaire_net_desire"] == 400000
        assert result["salaire_brut_requis"] > 400000

    def test_calculate_gross_from_net_accuracy(self):
        """Test that net->gross->net conversion is accurate"""
        desired_net = 300000
        gross_result = calculate_gross_from_net(desired_net)
        calculated_gross = gross_result["salaire_brut_requis"]
        
        # Convert back to net
        net_result = calculate_tax_details(calculated_gross)
        final_net = net_result["salaire_net"]
        
        # Should be very close (within 1% tolerance)
        tolerance = desired_net * 0.01
        assert abs(final_net - desired_net) <= tolerance

    def test_get_max_net_salary(self):
        """Test dynamic calculation of maximum net salary"""
        max_net = get_max_net_salary()
        
        # Should be a positive number less than gross
        assert max_net > 0
        assert max_net < MAX_GROSS_SALARY
        
        # Should be consistent when called multiple times
        assert get_max_net_salary() == max_net

    def test_get_salary_limits(self):
        """Test salary limits utility function"""
        limits = get_salary_limits()
        
        # Should have required keys
        assert "max_gross" in limits
        assert "max_net" in limits
        assert "formatted" in limits
        
        # Should have formatted versions
        assert "max_gross" in limits["formatted"]
        assert "max_net" in limits["formatted"]
        
        # Formatted should contain fCFA
        assert "fCFA" not in limits["formatted"]["max_gross"]  # French formatting uses dots, not fCFA
        assert isinstance(limits["max_gross"], int)
        assert isinstance(limits["max_net"], int)

class TestAPIEndpoints:
    
    @patch('main.make_response')
    @patch('main.jsonify')
    @patch('main.log_to_sheet')
    @patch('main.check_rate_limit')
    def test_main_gross_calculation(self, mock_rate_limit, mock_log, mock_jsonify, mock_make_response):
        """Test main function with gross salary input"""
        mock_rate_limit.return_value = True
        
        # Mock Flask functions
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.data = json.dumps({"salaire_brut": 500000, "salaire_net": 400000})
        mock_response.headers = Mock()
        mock_response.headers.add = Mock()
        mock_make_response.return_value = mock_response
        mock_jsonify.return_value = {"salaire_brut": 500000, "salaire_net": 400000}
        
        # Create mock request
        request = Mock()
        request.method = "POST"
        request.headers = {"X-Forwarded-For": "127.0.0.1"}
        request.get_json.return_value = {"brut": 500000}
        
        response = main(request)
        
        # Check response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "salaire_brut" in data
        assert "salaire_net" in data
        assert data["salaire_brut"] == 500000

    @patch('main.make_response')
    @patch('main.jsonify')
    @patch('main.log_to_sheet')
    @patch('main.check_rate_limit')
    def test_main_net_calculation(self, mock_rate_limit, mock_log, mock_jsonify, mock_make_response):
        """Test main function with net salary input"""
        mock_rate_limit.return_value = True
        
        # Mock Flask functions
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.data = json.dumps({"salaire_net_desire": 400000, "salaire_brut_requis": 500000})
        mock_response.headers = Mock()
        mock_response.headers.add = Mock()
        mock_make_response.return_value = mock_response
        mock_jsonify.return_value = {"salaire_net_desire": 400000, "salaire_brut_requis": 500000}
        
        # Create mock request
        request = Mock()
        request.method = "POST"
        request.headers = {"X-Forwarded-For": "127.0.0.1"}
        request.get_json.return_value = {"net": 400000}
        
        response = main(request)
        
        # Check response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "salaire_net_desire" in data
        assert "salaire_brut_requis" in data
        assert data["salaire_net_desire"] == 400000

    @patch('main.make_response')
    @patch('main.jsonify')
    @patch('main.log_to_sheet')
    @patch('main.check_rate_limit')
    def test_main_rate_limit_exceeded(self, mock_rate_limit, mock_log, mock_jsonify, mock_make_response):
        """Test rate limiting"""
        mock_rate_limit.return_value = False
        
        # Mock Flask functions
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.data = json.dumps({"error": "Doucement champion(ne)!"})
        mock_response.headers = Mock()
        mock_response.headers.add = Mock()
        mock_make_response.return_value = mock_response
        mock_jsonify.return_value = {"error": "Doucement champion(ne)!"}
        
        # Create mock request
        request = Mock()
        request.method = "POST"
        request.headers = {"X-Forwarded-For": "127.0.0.1"}
        request.get_json.return_value = {"brut": 500000}
        
        response = main(request)
        
        # Should return 429
        assert response.status_code == 429
        data = json.loads(response.data)
        assert "error" in data

    @patch('main.make_response')
    @patch('main.jsonify')
    @patch('main.log_to_sheet')
    @patch('main.check_rate_limit')
    def test_main_invalid_request(self, mock_rate_limit, mock_log, mock_jsonify, mock_make_response):
        """Test invalid request handling"""
        mock_rate_limit.return_value = True
        
        # Mock Flask functions
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.data = json.dumps({"error": "Champ brut ou net attendu"})
        mock_response.headers = Mock()
        mock_response.headers.add = Mock()
        mock_make_response.return_value = mock_response
        mock_jsonify.return_value = {"error": "Champ brut ou net attendu"}
        
        # Create mock request with invalid data
        request = Mock()
        request.method = "POST"
        request.headers = {"X-Forwarded-For": "127.0.0.1"}
        request.get_json.return_value = {"invalid": "data"}
        
        response = main(request)
        
        # Should return 400
        assert response.status_code == 400

    @patch('main.make_response')
    @patch('main.jsonify')
    @patch('main.log_to_sheet')
    @patch('main.check_rate_limit')
    def test_main_salary_too_high(self, mock_rate_limit, mock_log, mock_jsonify, mock_make_response):
        """Test salary limit validation"""
        mock_rate_limit.return_value = True
        
        # Mock Flask functions
        mock_response = Mock()
        mock_response.status_code = 422
        mock_response.data = json.dumps({"stop": "Montant trop élevé"})
        mock_response.headers = Mock()
        mock_response.headers.add = Mock()
        mock_make_response.return_value = mock_response
        mock_jsonify.return_value = {"stop": "Montant trop élevé"}
        
        # Create mock request with very high salary
        request = Mock()
        request.method = "POST"
        request.headers = {"X-Forwarded-For": "127.0.0.1"}
        request.get_json.return_value = {"brut": 20000000}  # 20M CFA
        
        response = main(request)
        
        # Should return 422
        assert response.status_code == 422
        data = json.loads(response.data)
        assert "stop" in data

    @patch('main.make_response')
    def test_main_cors_options(self, mock_make_response):
        """Test CORS preflight handling"""
        # Mock Flask functions
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = Mock()
        mock_response.headers.add = Mock()
        mock_response.headers.__contains__ = Mock(return_value=True)
        mock_make_response.return_value = mock_response
        
        # Create mock OPTIONS request
        request = Mock()
        request.method = "OPTIONS"
        
        response = main(request)
        
        # Should return 200 with CORS headers
        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" in response.headers
        assert "Access-Control-Allow-Methods" in response.headers

if __name__ == "__main__":
    pytest.main([__file__, "-v"])