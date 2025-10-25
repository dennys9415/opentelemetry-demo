const request = require('supertest');
const app = require('../../src/frontend/server');

describe('Frontend Service', () => {
  it('should return health status', async () => {
    const response = await request(app).get('/health');
    expect(response.status).toBe(200);
    expect(response.body.status).toBe('healthy');
  });

  it('should serve the demo page', async () => {
    const response = await request(app).get('/');
    expect(response.status).toBe(200);
    expect(response.text).toContain('OpenTelemetry Demo');
  });
});