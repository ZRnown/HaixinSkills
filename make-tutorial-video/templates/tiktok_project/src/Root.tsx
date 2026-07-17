import { Composition, staticFile } from "remotion";
import { CaptionedVideo } from "./CaptionedVideo";

// Each <Composition> is an entry in the sidebar!

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="CaptionedVideo"
      component={CaptionedVideo}
      width={1080}
      height={1920}
      fps={30}
      durationInFrames={1085}
      defaultProps={{
        src: staticFile("base_video.mp4"),
      }}
    />
  );
};
