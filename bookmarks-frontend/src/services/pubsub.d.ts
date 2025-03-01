declare module '@/services/pubsub' {
    export const PubSub: {
      subscribe: (event: string, callback: (payload: any) => void) => void;
      publish: (event: string, payload?: any) => void;
    };
  }