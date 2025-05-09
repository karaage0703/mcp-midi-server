declare module '@modelcontextprotocol/sdk' {
  export class FastMCP {
    constructor(name: string);
    tool(options: {
      name: string;
      description: string;
      parameters: any;
      handler: (params: any) => Promise<string>;
    }): void;
    run(): void;
  }
}
