import sharp from 'sharp';
import path from 'path';

export const generateThumbnail = async (filePath: string) => {
  const ext = path.extname(filePath);
  const thumbName = filePath.replace(ext, `_thumb${ext}`);
  await sharp(filePath).resize(300, 300, { fit: 'inside' }).toFile(thumbName);
  return thumbName;
};
