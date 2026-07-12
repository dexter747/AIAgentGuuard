import {
  IExecuteFunctions,
  INodeExecutionData,
  INodeType,
  INodeTypeDescription,
  NodeApiError,
} from 'n8n-workflow';

export class OverseeX implements INodeType {
  description: INodeTypeDescription = {
    displayName: 'OverseeX',
    name: 'overseeX',
    icon: 'file:overseex.svg',
    group: ['transform'],
    version: 1,
    subtitle: '={{$parameter["operation"] + ": " + $parameter["resource"]}}',
    description: 'AI Agent Monitoring & Testing with OverseeX',
    defaults: {
      name: 'OverseeX',
    },
    inputs: ['main'],
    outputs: ['main'],
    credentials: [
      {
        name: 'overseeXApi',
        required: true,
      },
    ],
    properties: [
      {
        displayName: 'Resource',
        name: 'resource',
        type: 'options',
        noDataExpression: true,
        options: [
          {
            name: 'Agent',
            value: 'agent',
          },
          {
            name: 'Trace',
            value: 'trace',
          },
          {
            name: 'Coordination',
            value: 'coordination',
          },
        ],
        default: 'trace',
      },

      // Agent Operations
      {
        displayName: 'Operation',
        name: 'operation',
        type: 'options',
        noDataExpression: true,
        displayOptions: {
          show: {
            resource: ['agent'],
          },
        },
        options: [
          {
            name: 'Create',
            value: 'create',
            description: 'Create a new agent',
            action: 'Create an agent',
          },
          {
            name: 'Get',
            value: 'get',
            description: 'Get an agent by ID',
            action: 'Get an agent',
          },
          {
            name: 'List',
            value: 'list',
            description: 'List all agents',
            action: 'List agents',
          },
        ],
        default: 'list',
      },

      // Trace Operations
      {
        displayName: 'Operation',
        name: 'operation',
        type: 'options',
        noDataExpression: true,
        displayOptions: {
          show: {
            resource: ['trace'],
          },
        },
        options: [
          {
            name: 'Create',
            value: 'create',
            description: 'Create a new trace',
            action: 'Create a trace',
          },
          {
            name: 'Get',
            value: 'get',
            description: 'Get a trace by ID',
            action: 'Get a trace',
          },
          {
            name: 'List',
            value: 'list',
            description: 'List traces',
            action: 'List traces',
          },
        ],
        default: 'create',
      },

      // Coordination Operations
      {
        displayName: 'Operation',
        name: 'operation',
        type: 'options',
        noDataExpression: true,
        displayOptions: {
          show: {
            resource: ['coordination'],
          },
        },
        options: [
          {
            name: 'Analyze',
            value: 'analyze',
            description: 'Analyze traces for coordination issues',
            action: 'Analyze coordination',
          },
          {
            name: 'Get Issues',
            value: 'getIssues',
            description: 'Get coordination issues',
            action: 'Get coordination issues',
          },
          {
            name: 'Get Suggestions',
            value: 'getSuggestions',
            description: 'Get ML-powered suggestions',
            action: 'Get suggestions',
          },
        ],
        default: 'getIssues',
      },

      // Agent Create Fields
      {
        displayName: 'Agent Name',
        name: 'agentName',
        type: 'string',
        default: '',
        required: true,
        displayOptions: {
          show: {
            resource: ['agent'],
            operation: ['create'],
          },
        },
        description: 'Name of the agent to create',
      },
      {
        displayName: 'Description',
        name: 'description',
        type: 'string',
        default: '',
        displayOptions: {
          show: {
            resource: ['agent'],
            operation: ['create'],
          },
        },
        description: 'Description of the agent',
      },

      // Agent Get Fields
      {
        displayName: 'Agent ID',
        name: 'agentId',
        type: 'string',
        default: '',
        required: true,
        displayOptions: {
          show: {
            resource: ['agent'],
            operation: ['get'],
          },
        },
        description: 'ID of the agent to retrieve',
      },

      // Trace Create Fields
      {
        displayName: 'Agent ID',
        name: 'traceAgentId',
        type: 'string',
        default: '',
        required: true,
        displayOptions: {
          show: {
            resource: ['trace'],
            operation: ['create'],
          },
        },
        description: 'ID of the agent for this trace',
      },
      {
        displayName: 'Input Data',
        name: 'inputData',
        type: 'json',
        default: '{}',
        required: true,
        displayOptions: {
          show: {
            resource: ['trace'],
            operation: ['create'],
          },
        },
        description: 'Input data for the trace (JSON)',
      },
      {
        displayName: 'Output Data',
        name: 'outputData',
        type: 'json',
        default: '{}',
        displayOptions: {
          show: {
            resource: ['trace'],
            operation: ['create'],
          },
        },
        description: 'Output data for the trace (JSON)',
      },
      {
        displayName: 'Status',
        name: 'status',
        type: 'options',
        options: [
          { name: 'Success', value: 'success' },
          { name: 'Error', value: 'error' },
          { name: 'Failed', value: 'failed' },
        ],
        default: 'success',
        displayOptions: {
          show: {
            resource: ['trace'],
            operation: ['create'],
          },
        },
        description: 'Status of the trace',
      },
      {
        displayName: 'Duration (ms)',
        name: 'durationMs',
        type: 'number',
        default: 0,
        displayOptions: {
          show: {
            resource: ['trace'],
            operation: ['create'],
          },
        },
        description: 'Duration of the trace in milliseconds',
      },

      // Trace Get Fields
      {
        displayName: 'Trace ID',
        name: 'traceId',
        type: 'string',
        default: '',
        required: true,
        displayOptions: {
          show: {
            resource: ['trace'],
            operation: ['get'],
          },
        },
        description: 'ID of the trace to retrieve',
      },

      // Trace List Fields
      {
        displayName: 'Agent ID (Filter)',
        name: 'listAgentId',
        type: 'string',
        default: '',
        displayOptions: {
          show: {
            resource: ['trace'],
            operation: ['list'],
          },
        },
        description: 'Filter traces by agent ID',
      },
      {
        displayName: 'Limit',
        name: 'limit',
        type: 'number',
        default: 50,
        displayOptions: {
          show: {
            resource: ['trace', 'coordination'],
            operation: ['list', 'getIssues', 'getSuggestions'],
          },
        },
        description: 'Maximum number of results to return',
      },

      // Coordination Analyze Fields
      {
        displayName: 'Trace IDs',
        name: 'analyzeTraceIds',
        type: 'string',
        default: '',
        displayOptions: {
          show: {
            resource: ['coordination'],
            operation: ['analyze'],
          },
        },
        description: 'Comma-separated list of trace IDs to analyze',
      },
    ],
  };

  async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
    const items = this.getInputData();
    const returnData: INodeExecutionData[] = [];
    const credentials = await this.getCredentials('overseeXApi');

    const baseUrl = (credentials.baseUrl as string) || 'https://api.overseex.com';
    const resource = this.getNodeParameter('resource', 0) as string;
    const operation = this.getNodeParameter('operation', 0) as string;

    for (let i = 0; i < items.length; i++) {
      try {
        let endpoint = '';
        let method = 'GET';
        let body: any = undefined;

        // Agent operations
        if (resource === 'agent') {
          if (operation === 'create') {
            endpoint = '/api/v1/agents';
            method = 'POST';
            body = {
              name: this.getNodeParameter('agentName', i) as string,
              description: this.getNodeParameter('description', i) as string,
            };
          } else if (operation === 'get') {
            const agentId = this.getNodeParameter('agentId', i) as string;
            endpoint = `/api/v1/agents/${agentId}`;
          } else if (operation === 'list') {
            endpoint = '/api/v1/agents';
          }
        }

        // Trace operations
        if (resource === 'trace') {
          if (operation === 'create') {
            endpoint = '/api/v1/traces';
            method = 'POST';
            body = {
              agent_id: this.getNodeParameter('traceAgentId', i) as string,
              input_data: JSON.parse(this.getNodeParameter('inputData', i) as string),
              output_data: JSON.parse(this.getNodeParameter('outputData', i) as string),
              status: this.getNodeParameter('status', i) as string,
              total_duration_ms: this.getNodeParameter('durationMs', i) as number,
              metadata: { source: 'n8n' },
              tags: ['n8n'],
            };
          } else if (operation === 'get') {
            const traceId = this.getNodeParameter('traceId', i) as string;
            endpoint = `/api/v1/traces/${traceId}`;
          } else if (operation === 'list') {
            const agentId = this.getNodeParameter('listAgentId', i) as string;
            const limit = this.getNodeParameter('limit', i) as number;
            endpoint = `/api/v1/traces?limit=${limit}`;
            if (agentId) {
              endpoint += `&agent_id=${agentId}`;
            }
          }
        }

        // Coordination operations
        if (resource === 'coordination') {
          if (operation === 'analyze') {
            endpoint = '/api/v1/coordination/analyze';
            method = 'POST';
            const traceIdsStr = this.getNodeParameter('analyzeTraceIds', i) as string;
            body = {
              trace_ids: traceIdsStr.split(',').map(id => id.trim()),
              auto_create_issues: true,
            };
          } else if (operation === 'getIssues') {
            const limit = this.getNodeParameter('limit', i) as number;
            endpoint = `/api/v1/coordination/issues?limit=${limit}`;
          } else if (operation === 'getSuggestions') {
            const limit = this.getNodeParameter('limit', i) as number;
            endpoint = `/api/v1/coordination/suggestions?limit=${limit}`;
          }
        }

        // Make request
        const options: any = {
          method,
          uri: `${baseUrl}${endpoint}`,
          headers: {
            'Authorization': `Bearer ${credentials.apiKey}`,
            'Content-Type': 'application/json',
          },
          json: true,
        };

        if (body) {
          options.body = body;
        }

        const response = await this.helpers.request(options);

        returnData.push({
          json: response,
          pairedItem: { item: i },
        });
      } catch (error) {
        if (this.continueOnFail()) {
          returnData.push({
            json: { error: (error as Error).message },
            pairedItem: { item: i },
          });
          continue;
        }
        throw new NodeApiError(this.getNode(), { message: (error as Error).message });
      }
    }

    return [returnData];
  }
}
