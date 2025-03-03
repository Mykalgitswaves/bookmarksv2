declare module '@/services/urls' {
    export const urls: {
      reviews: {
        getComments: (postId: string) => string;
        getCommentForComments: (postId: string, commentId: string) => string;
        getParentCommentsForComment: (postId: string, commentId: string) => string;
        likeComment: (commentId: string) => string;
      };
      bookclubs: {
        getClubFeed: (clubId: string) => string;
      };
      user: {
        getUser: (userId: string) => string;
      };
      concatQueryParams: (url: string, params: Record<string, any>) => string;
    };
  
    export const navRoutes: {
      toBookClubFeed: (userId: string, clubId: string) => string;
      toBookClubCommentPage: (userId: string, clubId: string, postId: string) => string;
      toSubThreadPage: (userId: string, clubId: string, postId: string, threadId: string) => string;
    };
  }