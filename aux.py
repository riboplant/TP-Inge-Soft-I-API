{'status': 200, 
 'response': {'accounts_info': None, 
              'acquirer_reconciliation': [], 
              'additional_info': {'authentication_code': None, 
                                  'available_balance': None, 
                                  'ip_address': '181.46.160.41', 
                                  'items': [{'category_id': None, 
                                             'description': None, 
                                             'id': None, 
                                             'picture_url': None, 
                                             'quantity': '1', 
                                             'title': 'asdasdasda', 
                                             'unit_price': '10'
                                             }], 
                                   'nsu_processadora': None
                                   }, 
              'authorization_code': None, 
              'binary_mode': False, 
              'brand_id': None, 
              'build_version': '3.74.0-rc-3', 
              'call_for_authorize_id': None, 
              'captured': True, 
              'card': {}, 
              'charges_details': [{'accounts': {'from': 'collector', 
                                                'to': 'mp'
                                                }, 
                                   'amounts': {'original': 0.41, 
                                               'refunded': 0
                                               }, 
                                   'client_id': 0, 
                                   'date_created': '2024-10-17T15:03:59.000-04:00', 
                                   'id': '90819405002-001', 
                                   'last_updated': '2024-10-17T15:03:59.000-04:00', 
                                   'metadata': {'source': 'rule-engine'}, 
                                   'name': 'mercadopago_fee', 
                                   'refund_charges': [], 
                                   'reserve_id': None, 
                                   'type': 'fee'
                                   }], 
              'collector_id': 2018940061, 
              'corporation_id': None, 
              'counter_currency': None, 
              'coupon_amount': 0, 
              'currency_id': 'ARS', 
              'date_approved': '2024-10-17T15:03:59.000-04:00', 
              'date_created': '2024-10-17T15:03:59.000-04:00', 
              'date_last_updated': '2024-10-17T15:03:59.000-04:00', 
              'date_of_expiration': None, 
              'deduction_schema': None,
              'description': 'asdasdasda', 
              'differential_pricing_id': None, 
              'external_reference': None, 
              'fee_details': [{'amount': 0.41, 
                               'fee_payer': 'collector', 
                               'type': 'mercadopago_fee'
                               }], 
              'financing_group': None, 
              'id': 90819405002, 
              'installments': 1, 
              'integrator_id': None, 
              'issuer_id': '2005', 
              'live_mode': True, 
              'marketplace_owner': None, 
              'merchant_account_id': None, 
              'merchant_number': None, 
              'metadata': {'info': 'test'}, 
              'money_release_date': '2024-11-04T15:03:59.000-04:00', 
              'money_release_schema': None, 
              'money_release_status': 'pending', 
              'notification_url': None, 
              'operation_type': 'regular_payment', 
              'order': {'id': '24006589130', 
                        'type': 'mercadopago'}, 
              'payer': {'email': 'test_user_1112138976@testuser.com', 
                        'entity_type': None, 
                        'first_name': None, 
                        'id': '2021626354', 
                        'identification': {'number': '1111111', 
                                           'type': 'DNI'}, 
                        'last_name': None, 
                        'operator_id': None, 
                        'phone': {'number': None, 
                                  'extension': None, 
                                  'area_code': None
                                  }, 
                        'type': None
                        }, 
              'payment_method': {'id': 'account_money', 
                                 'issuer_id': '2005', 
                                 'type': 'account_money'
                                 }, 
              'payment_method_id': 'account_money', 
              'payment_type_id': 'account_money', 
              'platform_id': None, 
              'point_of_interaction': {'business_info': {'branch': 'Merchant Services', 
                                                         'sub_unit': 'checkout_pro', 
                                                         'unit': 'online_payments'
                                                         }, 
                                       'transaction_data': {'e2e_id': None}, 
                                       'type': 'CHECKOUT'
                                       }, 
              'pos_id': None, 
              'processing_mode': 
              'aggregator', 
              'refunds': [], 
              'release_info': None, 
              'shipping_amount': 0, 
              'sponsor_id': None, 
              'statement_descriptor': None, 
              'status': 'approved', 
              'status_detail': 'accredited', 
              'store_id': None, 
              'tags': None, 
              'taxes_amount': 0, 
              'transaction_amount': 10, 
              'transaction_amount_refunded': 0, 
              'transaction_details': {'acquirer_reference': None, 
                                      'external_resource_url': None, 
                                      'financial_institution': None, 
                                      'installment_amount': 0, 
                                      'net_received_amount': 9.59, 
                                      'overpaid_amount': 0, 
                                      'payable_deferral_period': None, 
                                      'payment_method_reference_id': None, 
                                      'total_paid_amount': 10
                                      }
                  }
}