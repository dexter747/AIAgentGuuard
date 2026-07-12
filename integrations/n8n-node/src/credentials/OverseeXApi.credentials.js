"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.OverseeXApi = void 0;
class OverseeXApi {
    constructor() {
        this.name = 'overseeXApi';
        this.displayName = 'OverseeX API';
        this.documentationUrl = 'https://docs.overseex.com/integrations/n8n';
        this.properties = [
            {
                displayName: 'API Key',
                name: 'apiKey',
                type: 'string',
                typeOptions: {
                    password: true,
                },
                default: '',
                required: true,
                description: 'Your OverseeX API key (starts with ag_live_ or ag_test_)',
            },
            {
                displayName: 'Base URL',
                name: 'baseUrl',
                type: 'string',
                default: 'https://api.overseex.com',
                description: 'OverseeX API base URL',
            },
        ];
        this.authenticate = {
            type: 'generic',
            properties: {
                headers: {
                    Authorization: '=Bearer {{$credentials.apiKey}}',
                },
            },
        };
    }
}
exports.OverseeXApi = OverseeXApi;
